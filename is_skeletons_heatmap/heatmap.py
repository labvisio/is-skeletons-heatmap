from collections import deque
from typing import List, TypedDict

import cv2
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy
from is_msgs.image_pb2 import Image, ObjectAnnotation, ObjectAnnotations

from is_skeletons_heatmap.conf.options_pb2 import RotateFlags, SkeletonsHeatmapOptions
from is_skeletons_heatmap.logger import Logger
from is_skeletons_heatmap.transformation import (
    TransformationFetcher,
    transform_object_annotations,
)
from is_skeletons_heatmap.utils import array2image


class Coordinates(TypedDict):
    x: list
    y: list


class SkeletonsHeatmap:
    def __init__(self, options: SkeletonsHeatmapOptions) -> None:
        self.log = Logger("SkeletonsHeatmap")
        self._options = options
        fh, fv = self._options.flip_horizontal, self._options.flip_vertical
        self._flip = fh or fv
        self._flip_code = -1 if fh and fv else (1 if fh and not fv else 0)
        x_bins = np.arange(
            start=self._options.limits.xmin,
            stop=self._options.limits.xmax,
            step=self._options.bins_step,
        )
        y_bins = np.arange(
            start=self._options.limits.ymin,
            stop=self._options.limits.ymax,
            step=self._options.bins_step,
        )
        self._bins = (x_bins, y_bins)
        size = (y_bins.size - 1, x_bins.size - 1)
        self._dx = self._options.limits.xmax - self._options.limits.xmin
        self._dy = self._options.limits.ymax - self._options.limits.ymin
        self._lin_histogram = np.zeros(shape=size, dtype=np.float64)
        self._cmap = plt.cm.jet_r
        self._scale = self._options.output_scale.value
        self._white = (255, 255, 255)
        self._red = (0, 0, 255)
        self._green = (0, 255, 0)
        self._image_histogram = np.empty(shape=1, dtype=np.uint8)
        if self._options.samples > 100000:
            self.log.critical("Number of samples must be less or equal than 100000.")
        self._infinity_mode = self._options.samples < 1
        maxlen = max(0, self._options.samples)
        self._sparse_histograms = deque(iterable=[], maxlen=maxlen)
        self._tf_fetcher = TransformationFetcher(broker_uri=self._options.broker_uri)

    def update_heatmap(self, list_annotations: List[ObjectAnnotations]) -> None:
        coordinates = Coordinates(x=[], y=[])
        average = self._options.average_coordinates
        for skeletons in list_annotations:
            src, dst = skeletons.frame_id, self._options.frame_id
            if src != dst:
                transformation = self._tf_fetcher.get_transformation(src, dst)
                if transformation is None:
                    continue
                skeletons = transform_object_annotations(skeletons, transformation, dst)
            for skeleton in skeletons.objects:
                coordinates["x"].extend(self._get_coordinate(skeleton, "x", average))
                coordinates["y"].extend(self._get_coordinate(skeleton, "y", average))

        histogram, _, _ = np.histogram2d(
            x=np.array(coordinates["x"]),
            y=np.array(coordinates["y"]),
            bins=self._bins,
        )
        self._sparse_histograms.append(scipy.sparse.csr_matrix(histogram.T))
        self._lin_histogram += histogram.T
        if not self._infinity_mode:
            oldest_h = scipy.sparse.csr_matrix.todense(self._sparse_histograms[0])
            self._lin_histogram -= oldest_h
        if self._options.log_scale:
            self._lin_histogram = np.clip(self._lin_histogram, a_min=1.0, a_max=None)
            final = np.log10(self._lin_histogram)
        else:
            final = self._lin_histogram

        norm = plt.Normalize(vmin=final.min(), vmax=final.max())
        self._image_histogram = (255 * self._cmap(norm(final))[:, :, :-1]).astype(
            np.uint8
        )

        if self._options.HasField("output_scale"):
            self._image_histogram = cv2.resize(
                src=self._image_histogram,
                dsize=(0, 0),
                fx=self._scale,
                fy=self._scale,
            )
        if self._options.draw_grid:
            self._draw_grid()
        if self._options.HasField("referential"):
            self._draw_referential()
        if self._flip:
            self._image_histogram = cv2.flip(
                src=self._image_histogram,
                flipCode=self._flip_code,
            )
        if self._options.output_rotate != RotateFlags.Value("NONE"):
            self._image_histogram = cv2.rotate(
                src=self._image_histogram,
                rotateCode=self._options.output_rotate - 1,
            )

    def get_np_image(self) -> npt.NDArray[np.uint8]:
        return self._image_histogram

    def get_pb_image(self) -> Image:
        return array2image(
            input_image=self._image_histogram,
            encode_format=".jpeg",
            compression_level=0.8,
        )

    def _get_coordinate(
        self,
        skeleton: ObjectAnnotation,
        axis: str,
        mean: bool = False,
    ) -> List[float]:
        coordinates = [
            getattr(keypoint.position, axis) for keypoint in skeleton.keypoints
        ]
        return [np.mean(np.array(coordinates))] if mean else coordinates

    def _draw_grid(self) -> None:
        steps = lambda smin, smax: np.arange(np.floor(smin), np.ceil(smax) + 1.0, 1.0)
        xmin, xmax = self._options.limits.xmin, self._options.limits.xmax
        ymin, ymax = self._options.limits.ymin, self._options.limits.ymax
        height, width, _ = self._image_histogram.shape
        x_steps = width * (steps(xmin, xmax) - xmin) / self._dx
        y_steps = height * (steps(ymin, ymax) - ymin) / self._dy
        for x in map(int, x_steps):
            self._image_histogram = cv2.line(
                img=self._image_histogram,
                pt1=(x, 0),
                pt2=(x, height),
                color=self._white,
            )
        for y in map(int, y_steps):
            self._image_histogram = cv2.line(
                img=self._image_histogram,
                pt1=(0, y),
                pt2=(width, y),
                color=self._white,
            )

    def _draw_referential(self) -> None:
        xmin, _ = self._options.limits.xmin, self._options.limits.xmax
        ymin, _ = self._options.limits.ymin, self._options.limits.ymax
        width, height = self._image_histogram.shape[1], self._image_histogram.shape[0]
        px = int(width * (self._options.referential.x - xmin) / self._dx)
        py = int(height * (self._options.referential.y - ymin) / self._dy)
        length = self._options.referential.length
        pt1, pt2_x, pt2_y = (px, py), (px + length, py), (px, py + length)
        self._image_histogram = cv2.arrowedLine(
            img=self._image_histogram,
            pt1=pt1,
            pt2=pt2_x,
            color=self._red,
            thickness=3,
            tipLength=0.2,
        )
        self._image_histogram = cv2.arrowedLine(
            img=self._image_histogram,
            pt1=pt1,
            pt2=pt2_y,
            color=self._green,
            thickness=3,
            tipLength=0.2,
        )
