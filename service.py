from __future__ import print_function

from is_msgs.image_pb2 import ObjectAnnotations
from is_wire.core import Channel, Message, Subscription, Logger
from is_wire.core import ZipkinTracer
from utils import load_options
from heatmap import SkeletonsHeatmap

log = Logger()
ops = load_options()

c = Channel(ops.broker_uri)
sb = Subscription(c)
service_name = 'Skeletons.Heatmap'
tracer = ZipkinTracer(host_name=ops.zipkin_host,
                      port=ops.zipkin_port, service_name=service_name)

sks_hm = SkeletonsHeatmap(ops)

@tracer.interceptor('Render')
def on_detections(msg, context):
    sks = msg.unpack(ObjectAnnotations)
    sks_hm.update_heatmap(sks)
    im_pb = sks_hm.get_pb_image()
    msg = Message()
    msg.pack(im_pb)
    msg.set_topic(service_name)
    msg.add_metadata(context)
    c.publish(msg)

sb.subscribe('Skeletons.Localization', on_detections)
c.listen()