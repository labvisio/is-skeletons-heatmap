import cv2
import numpy as np
from scipy import sparse
import matplotlib.pyplot as plt
from collections import deque

from is_msgs.image_pb2 import ObjectAnnotations
from .options_pb2 import SkeletonsHeatmapOptions, RotateFlags
from .utils import to_pb_image
from .transformation import TransformationFetcher, transform_object_annotations

class SkeletonsHeatmap:
    def __init__(self, options):
        if not isinstance(options, SkeletonsHeatmapOptions):
            msg = 'Invalid options type: \'{}\'. Must be an object of \'{}\''.format(
                type(options), SkeletonsHeatmapOptions.DESCRIPTOR.full_name)
            raise Exception(msg)
        self._op = options
        fh, fv = self._op.flip_horizontal, self._op.flip_vertical
        self._flip = fh or fv
        self._flip_code = -1 if fh and fv else (1 if fh and not fv else 0)
        x_bins = np.arange(self._op.limits.xmin, self._op.limits.xmax, self._op.bins_step)
        y_bins = np.arange(self._op.limits.ymin, self._op.limits.ymax, self._op.bins_step)
        self._bins = (x_bins, y_bins)
        size = (y_bins.size - 1, x_bins.size - 1)
        self._dx = self._op.limits.xmax - self._op.limits.xmin
        self._dy = self._op.limits.ymax - self._op.limits.ymin
        self._linH = np.zeros(size, dtype=np.float64)
        self._cmap = plt.cm.jet_r
        self._scale = self._op.output_scale.value
        self._white = (255, 255, 255)
        self._red = (0, 0, 255)
        self._green = (0, 255, 0)
        self._imH = np.empty(1, dtype=np.uint8)
        if self._op.samples > 100000:
            raise Exception('Number of samples must be less or equal than 100000.')
        self._infinity_mode = self._op.samples < 1
        maxlen = max(0, self._op.samples)
        self._sparse_histograms = deque([], maxlen=maxlen)
        self._tf_fetcher = TransformationFetcher(self._op.broker_uri)


    def update_heatmap(self, skeletons):
        exception_msg = "Invalid type. Can be either a list of "
        exception_msg += "'ObjectAnnotations' or a single 'ObjectAnnotations'"
        
        if isinstance(skeletons, list):
            if not all(map(lambda x: isinstance(x, ObjectAnnotations), skeletons)):
                exception_msg += "\n Given a list containing at least one "
                exception_msg += "that isn't an 'ObjectAnnotations'"
                raise RuntimeError(exception_msg)
        elif not isinstance(skeletons, ObjectAnnotations):
            exception_msg += "\nGiven a {}".format(type(skeletons))
            raise RuntimeError(exception_msg)
        

        if isinstance(skeletons, ObjectAnnotations): 
            list_annotations = [skeletons]
        else :
            list_annotations = skeletons
        
        x, y = [], []
        avg = self._op.average_coordinates
        for skeletons in list_annotations:
            _from, _to = skeletons.frame_id, self._op.frame_id
            if _from != _to:
                tf = self._tf_fetcher.get_transformation(_from, _to)
                if tf is None:
                    continue
                skeletons = transform_object_annotations(skeletons, tf, _to)
            for sk in skeletons.objects:
                x.extend(self._get_coordinate(sk, 'x', avg))
                y.extend(self._get_coordinate(sk, 'y', avg))
        
        h, _, _ = np.histogram2d(np.array(x), np.array(y), bins=self._bins)
        self._sparse_histograms.append(sparse.csr_matrix(h.T))
        self._linH += h.T
        if not self._infinity_mode:
            oldest_h = sparse.csr_matrix.todense(self._sparse_histograms[0])
            self._linH -= oldest_h
        if self._op.log_scale:
            self._linH = np.clip(self._linH, a_min=1.0, a_max=None)
            H = np.log10(self._linH)
        else: 
            H = self._linH
        
        norm = plt.Normalize(vmin=H.min(), vmax=H.max())
        self._imH = (255 * self._cmap(norm(H))[:, :, :-1]).astype(np.uint8)

        if self._op.HasField('output_scale'):
            self._imH = cv2.resize(
                src=self._imH, 
                dsize=(0, 0), 
                fx=self._scale, 
                fy=self._scale
            )
        if self._op.draw_grid:
            self._draw_grid()
        if self._op.HasField('referential'):
            self._draw_referential()
        if self._flip:
            self._imH = cv2.flip(self._imH, self._flip_code)
        if self._op.output_rotate != RotateFlags.Value('NONE'):
            self._imH = cv2.rotate(self._imH, self._op.output_rotate - 1)


    def get_np_image(self):
        return self._imH


    def get_pb_image(self):
        return to_pb_image(self._imH)


    def _get_coordinate(self, sk, axis, mean=False):
        def reducer(p): return getattr(getattr(p, 'position'), axis)
        coordinates = [reducer(kp) for kp in sk.keypoints]
        return [np.mean(np.array(coordinates))] if mean else coordinates


    def _draw_grid(self):
        steps = lambda smin, smax: np.arange(np.floor(smin), np.ceil(smax) + 1.0, 1.0)
        xmin, xmax = self._op.limits.xmin, self._op.limits.xmax
        ymin, ymax = self._op.limits.ymin, self._op.limits.ymax
        width, height = self._imH.shape[1], self._imH.shape[0]
        x_steps = width * (steps(xmin, xmax) - xmin) / self._dx
        y_steps = height * (steps(ymin, ymax) - ymin) / self._dy
        for x in map(int, x_steps):
            self._imH = cv2.line(self._imH, pt1=(x, 0), pt2=(x, height), color=self._white)
        for y in map(int, y_steps):
            self._imH = cv2.line(self._imH, pt1=(0, y), pt2=(width, y), color=self._white)


    def _draw_referential(self):
        xmin, xmax = self._op.limits.xmin, self._op.limits.xmax
        ymin, ymax = self._op.limits.ymin, self._op.limits.ymax
        width, height = self._imH.shape[1], self._imH.shape[0]
        px = int(width * (self._op.referential.x - xmin) / self._dx)
        py = int(height * (self._op.referential.y - ymin) / self._dy)
        length = self._op.referential.length
        pt1, pt2_x, pt2_y = (px, py), (px + length, py), (px, py + length)
        self._imH = cv2.arrowedLine(self._imH, pt1=pt1, pt2=pt2_x, color=self._red, thickness=3, tipLength=0.2)
        self._imH = cv2.arrowedLine(self._imH, pt1=pt1, pt2=pt2_y, color=self._green, thickness=3, tipLength=0.2)