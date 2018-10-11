from __future__ import print_function

import dateutil.parser as dp
from builtins import super

from is_msgs.image_pb2 import ObjectAnnotations
from is_wire.core import Channel, Message, Subscription, Logger
from is_wire.core import Tracer, ZipkinExporter, BackgroundThreadTransport
from is_wire.core.utils import now

from .utils import load_options
from .heatmap import SkeletonsHeatmap


def span_duration_ms(span):
    dt = dp.parse(span.end_time) - dp.parse(span.start_time)
    return dt.total_seconds() * 1000.0


class MyChannel(Channel):
    def consume_until(self, deadline):
        timeout = max([deadline - now(), 0.0])
        return super().consume(timeout=timeout)


service_name = 'SkeletonsHeatmap'
log = Logger(name=service_name)
ops = load_options()

channel = MyChannel(ops.broker_uri)
subscription = Subscription(channel, name='{}.Render'.format(service_name))
exporter = ZipkinExporter(
    service_name=service_name,
    host_name=ops.zipkin_host,
    port=ops.zipkin_port,
    transport=BackgroundThreadTransport(max_batch_size=20),
)

for group_id in ops.group_ids:
    subscription.subscribe('SkeletonsGrouper.{}.Localization'.format(group_id))

sks_hm = SkeletonsHeatmap(ops)

period = ops.period_ms / 1000.0
deadline = now()
while True:
    deadline += period
    msgs = []
    while True:
        try:
            msgs.append(channel.consume_until(deadline=deadline))
        except:
            break

    span_context = msgs[-1].extract_tracing() if len(msgs) > 0 else None
    tracer = Tracer(exporter=exporter, span_context=span_context)
    update_span, service_span = None, None
    with tracer.span(name='Render') as span_0:
        sks_list = list(map(lambda x: x.unpack(ObjectAnnotations), msgs))
        with tracer.span(name='Update_Heatmap') as span_1:
            sks_hm.update_heatmap(sks_list)
            update_span = span_1
        im_pb = sks_hm.get_pb_image()
        msg = Message(content=im_pb)
        msg.inject_tracing(span_0)
        channel.publish(message=msg, topic='{}.Rendered'.format(service_name))
        service_span = span_0

    log.info('event=Render messages={}', len(msgs))
    log.info('took_ms= {{ update_heatmap={:4.2f}, service={:4.2f} }}',
             span_duration_ms(update_span), span_duration_ms(service_span))
