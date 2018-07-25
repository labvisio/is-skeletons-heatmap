from __future__ import print_function
import cv2
import json
import numpy as np
from is_msgs.image_pb2 import ObjectAnnotations
from is_wire.core import Channel, Message, Subscription, Logger
from is_wire.core import ZipkinTracer
import matplotlib.pyplot as plt
from utils import to_pb_image, get_coordinate, load_options

log = Logger()
ops = load_options()

c = Channel(ops.broker_uri)
sb = Subscription(c)
tracer = ZipkinTracer(host_name=ops.zipkin_host,
                      port=ops.zipkin_port, service_name='Skeletons_Heatmap')

x_min, x_max = ops.limits.xmin, ops.limits.xmax
y_min, y_max = ops.limits.ymin, ops.limits.ymax
step = ops.bins_step
avg_coordinates = ops.average_coordinates
scale = ops.output_scale
fh, fv = ops.flip_horizontal, ops.flip_vertical
flip = fh or fv
flip_code = -1 if fh and fv else (1 if fh and not fv else 0)

x_bins, y_bins = np.arange(x_min, x_max, step), np.arange(y_min, y_max, step)
linH = np.zeros((y_bins.size - 1, x_bins.size - 1), dtype=np.float64)
cmap = plt.cm.jet_r


@tracer.interceptor('Heatmap_{}'.format(ops.topic_id))
def on_detections(msg, context):
    global linH
    sks = msg.unpack(ObjectAnnotations)
    x, y = [], []
    for sk in sks.objects:
        x.extend(get_coordinate(sk, 'x', avg_coordinates))
        y.extend(get_coordinate(sk, 'y', avg_coordinates))
    x, y = np.array(x), np.array(y)
    h, _, _ = np.histogram2d(x, y, bins=(x_bins, y_bins))
    linH += h.T
    H = np.log10(linH + 1.0) if ops.log_scale else linH

    norm = plt.Normalize(vmin=H.min(), vmax=H.max())
    imH = 255 * cmap(norm(H))[:, :, :-1]
    imH = imH.astype(np.uint8)
    imH = cv2.resize(imH, dsize=(0, 0), fx=scale, fy=scale)

    width, height = imH.shape[1], imH.shape[0]
    dx, dy = x_max - x_min, y_max - y_min

    if ops.draw_grid:
        steps = lambda smin, smax: np.arange(np.floor(smin), np.ceil(smax) + 1.0, 1.0)
        x_steps = width * (steps(x_min, x_max) - x_min) / dx
        y_steps = height * (steps(y_min, y_max) - y_min) / dy
        white = (255, 255, 255)
        for x in map(int, x_steps):
            imH = cv2.line(imH, pt1=(x, 0), pt2=(x, height), color=white)
        for y in map(int, y_steps):
            imH = cv2.line(imH, pt1=(0, y), pt2=(width, y), color=white)

    if ops.HasField('referencial'):
        px = int(width * (ops.referencial.x - x_min) / dx)
        py = int(height * (ops.referencial.y - y_min) / dy)
        length = ops.referencial.length
        pt1, pt2_x, pt2_y = (px, py), (px + length, py), (px, py + length)
        red, green = (0, 0, 255), (0, 255, 0)
        imH = cv2.arrowedLine(imH, pt1=pt1, pt2=pt2_x, color=red, thickness=3, tipLength=0.2)
        imH = cv2.arrowedLine(imH, pt1=pt1, pt2=pt2_y, color=green, thickness=3, tipLength=0.2)

    if flip:
        imH = cv2.flip(imH, flip_code)

    im_pb = to_pb_image(imH)
    msg = Message()
    msg.pack(im_pb)
    msg.set_topic('Skeletons.{}.Heatmap'.format(ops.topic_id))
    msg.add_metadata(context)
    c.publish(msg)


sb.subscribe('Skeletons.{}.Detections'.format(ops.topic_id), on_detections)
c.listen()