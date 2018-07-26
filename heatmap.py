import cv2
import numpy as np
import matplotlib.pyplot as plt
from options_pb2 import SkeletonsHeatmapOptions
from is_msgs.image_pb2 import ObjectAnnotations
from utils import to_pb_image

class SkeletonsHeatmap:
    def __init__(self, options):
        if not isinstance(options, SkeletonsHeatmapOptions):
            msg = 'Invalid options type: \'{}\'. Must be an object of \'{}\''.format(
                type(options), SkeletonsHeatmapOptions.DESCRIPTOR.full_name)
            raise Exception(msg)
        self.__op = options
        fh, fv = self.__op.flip_horizontal, self.__op.flip_vertical
        self.__flip = fh or fv
        self.__flip_code = -1 if fh and fv else (1 if fh and not fv else 0)
        x_bins = np.arange(self.__op.limits.xmin, self.__op.limits.xmax, self.__op.bins_step)
        y_bins = np.arange(self.__op.limits.ymin, self.__op.limits.ymax, self.__op.bins_step)
        self.__bins = (x_bins, y_bins)
        size = (y_bins.size - 1, x_bins.size - 1)
        self.__dx = self.__op.limits.xmax - self.__op.limits.xmin
        self.__dy = self.__op.limits.ymax - self.__op.limits.ymin
        self.__linH = np.zeros(size, dtype=np.float64)
        self.__cmap = plt.cm.jet_r
        self.__scale = self.__op.output_scale
        self.__white = (255, 255, 255)
        self.__red = (0, 0, 255)
        self.__green = (0, 255, 0)
        self.__imH = np.empty(1, dtype=np.uint8)


    def update_heatmap(self, skeletons):
        x, y = [], []
        avg = self.__op.average_coordinates
        for sk in skeletons.objects:
            x.extend(self.__get_coordinate(sk, 'x', avg))
            y.extend(self.__get_coordinate(sk, 'y', avg))
        h, _, _ = np.histogram2d(np.array(x), np.array(y), bins=self.__bins)
        self.__linH += h.T
        H = np.log10(self.__linH + 1.0) if self.__op.log_scale else self.__linH
        norm = plt.Normalize(vmin=H.min(), vmax=H.max())
        self.__imH = (255 * self.__cmap(norm(H))[:, :, :-1]).astype(np.uint8)
        self.__imH = cv2.resize(self.__imH, dsize=(0, 0), fx=self.__scale, fy=self.__scale)

        if self.__op.draw_grid:
            self.__draw_grid()
        if self.__op.HasField('referencial'):
            self.__draw_referencial()
        if self.__flip:
            self.__imH = cv2.flip(self.__imH, self.__flip_code)


    def get_np_image(self):
        return self.__imH


    def get_pb_image(self):
        return to_pb_image(self.__imH)


    def __get_coordinate(self, sk, axis, mean=False):
        def reducer(p): return getattr(getattr(p, 'position'), axis)
        coordinates = [reducer(kp) for kp in sk.keypoints]
        return [np.mean(np.array(coordinates))] if mean else coordinates


    def __draw_grid(self):
        steps = lambda smin, smax: np.arange(np.floor(smin), np.ceil(smax) + 1.0, 1.0)
        xmin, xmax = self.__op.limits.xmin, self.__op.limits.xmax
        ymin, ymax = self.__op.limits.ymin, self.__op.limits.ymax
        width, height = self.__imH.shape[1], self.__imH.shape[0]
        x_steps = width * (steps(xmin, xmax) - xmin) / self.__dx
        y_steps = height * (steps(ymin, ymax) - ymin) / self.__dy
        for x in map(int, x_steps):
            self.__imH = cv2.line(self.__imH, pt1=(x, 0), pt2=(x, height), color=self.__white)
        for y in map(int, y_steps):
            self.__imH = cv2.line(self.__imH, pt1=(0, y), pt2=(width, y), color=self.__white)


    def __draw_referencial(self):
        xmin, xmax = self.__op.limits.xmin, self.__op.limits.xmax
        ymin, ymax = self.__op.limits.ymin, self.__op.limits.ymax
        width, height = self.__imH.shape[1], self.__imH.shape[0]
        px = int(width * (self.__op.referencial.x - xmin) / self.__dx)
        py = int(height * (self.__op.referencial.y - ymin) / self.__dy)
        length = self.__op.referencial.length
        pt1, pt2_x, pt2_y = (px, py), (px + length, py), (px, py + length)
        self.__imH = cv2.arrowedLine(self.__imH, pt1=pt1, pt2=pt2_x, color=self.__red, thickness=3, tipLength=0.2)
        self.__imH = cv2.arrowedLine(self.__imH, pt1=pt1, pt2=pt2_y, color=self.__green, thickness=3, tipLength=0.2)