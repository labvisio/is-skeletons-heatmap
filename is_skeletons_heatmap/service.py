import sys
from typing import List

import dateutil.parser as dp
from google.protobuf.json_format import Parse, ParseError
from is_msgs.image_pb2 import ObjectAnnotations
from is_wire.core import AsyncTransport, Message, Subscription, Tracer
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from opencensus.trace.span import Span

from is_skeletons_heatmap.channel import CustomChannel
from is_skeletons_heatmap.conf.options_pb2 import SkeletonsHeatmapOptions
from is_skeletons_heatmap.heatmap import SkeletonsHeatmap
from is_skeletons_heatmap.logger import Logger


def span_duration_ms(span: Span) -> float:
    interval = dp.parse(span.end_time) - dp.parse(span.start_time)
    return interval.total_seconds() * 1000.0


def unpack_all(messages: List[Message]) -> List[ObjectAnnotations]:
    return [message.unpack(ObjectAnnotations) for message in messages]


def load_options(logger: Logger) -> SkeletonsHeatmapOptions:
    op_file = (
        sys.argv[1] if len(sys.argv) > 1 else "/etc/is-skeletons-heatmap/options.json"
    )
    try:
        with open(op_file, "r", encoding="utf-8") as file:
            try:
                options = Parse(file.read(), SkeletonsHeatmapOptions())
                logger.info("Options: \n{}", options)
            except ParseError as ex:
                logger.critical("Unable to load options from '{}'. \n{}", op_file, ex)
    except FileNotFoundError:
        logger.critical("Unable to open file '{}'", op_file)

    message = options.DESCRIPTOR.full_name
    if options.period_ms < 200:
        message += " 'period_ms' field must be equal or greater than 200. "
        message += f"Given {options.period_ms}"
        logger.critical(message)
    if options.period_ms > 1000:
        message += " 'period_ms' field must be equal or less than 1000. "
        message += f"Given {options.period_ms}"
        logger.critical(message)
    return options


def main() -> None:
    service_name = "SkeletonsHeatmap"
    log = Logger(name=service_name)
    options = load_options(logger=log)
    channel = CustomChannel(uri=options.broker_uri, exchange="is")
    subscription = Subscription(channel=channel, name=f"{service_name}.Render")
    exporter = ZipkinExporter(
        service_name=service_name,
        host_name=options.zipkin_host,
        port=options.zipkin_port,
        transport=AsyncTransport,
    )
    for group_id in options.group_ids:
        subscription.subscribe(topic=f"SkeletonsGrouper.{group_id}.Localization")
    heatmap = SkeletonsHeatmap(options=options)
    period = options.period_ms / 1000.0

    while True:
        messages = channel.consume_for(period=period)
        span_context = messages[-1].extract_tracing() if len(messages) > 0 else None

        tracer = Tracer(exporter=exporter, span_context=span_context)
        span = tracer.start_span(name="render")
        update_span = None

        with tracer.span(name="unpack"):
            list_annotations = unpack_all(messages=messages)

        with tracer.span(name="update_heatmap") as _span:
            heatmap.update_heatmap(list_annotations=list_annotations)
            update_span = _span

        with tracer.span(name="pack_and_publish_heatmap"):
            im_pb = heatmap.get_pb_image()
            msg = Message(content=im_pb)
            msg.inject_tracing(span)
            channel.publish(message=msg, topic=f"{service_name}.Rendered")

        tracer.end_span()
        log.info("event=Render messages={}", len(messages))
        log.info(
            "took_ms= {{ update_heatmap={:4.2f}, service={:4.2f} }}",
            span_duration_ms(update_span),
            span_duration_ms(span),
        )


if __name__ == "__main__":
    main()
