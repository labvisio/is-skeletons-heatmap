import socket
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from is_msgs.camera_pb2 import FrameTransformation
from is_msgs.image_pb2 import ObjectAnnotations, Vertex
from is_wire.core import Channel, Subscription

from is_skeletons_heatmap.logger import Logger
from is_skeletons_heatmap.utils import array2vertex, tensor2array, vertex2array


def transform_vertex(vertex: Vertex, transformation: npt.NDArray[np.float32]):
    new_vertex = np.matmul(
        transformation,
        vertex2array(
            vertex=vertex,
            homogeneous=True,
        ),
    )
    return array2vertex(vertex=new_vertex)


def transform_object_annotations(
    annotations: ObjectAnnotations,
    transformation: npt.NDArray[np.float32],
    referential: int,
) -> ObjectAnnotations:
    new_objs = ObjectAnnotations(frame_id=referential)
    for obj in annotations.objects:
        new_obj = new_objs.objects.add()
        for keypoint in obj.keypoints:
            new_keypoint = new_obj.keypoints.add()
            new_keypoint.id = keypoint.id
            new_keypoint.position.CopyFrom(
                transform_vertex(keypoint.position, transformation)
            )
    return new_objs


class TransformationFetcher:
    def __init__(self, broker_uri: str):
        self.log = Logger("TransformationFetcher")
        self.channel = Channel(uri=broker_uri, exchange="is")
        self.subscription = Subscription(
            channel=self.channel,
            name="TransformationFetcher",
        )
        self.transformations = {}

    def get_transformation(self, src: int, dst: int) -> Optional[npt.NDArray[Any]]:
        if src in self.transformations and dst in self.transformations[src]:
            return self.transformations[src][dst]
        self.log.debug("event=RequestTranformation, from={}, to={}", src, dst)
        if self._request_transformation(src, dst):
            self.log.debug("event=ReceivedTranformation, from={}, to={}", src, dst)
            return self.transformations[src][dst]
        self.log.warn("event=FailedRequestTranformation, from={}, to={}", src, dst)
        return None

    def _request_transformation(self, src: int, dst: int) -> bool:
        topic = f"FrameTransformation.{src}.{dst}"
        self.subscription.subscribe(topic)
        try:
            msg = self.channel.consume(timeout=5.0)
            self.subscription.unsubscribe(topic)
        except socket.timeout:
            self.log.warn("event=Timeout, topic={}, timeout={}", topic, 5.0)
            self.subscription.unsubscribe(topic)
            return False
        transformation = msg.unpack(FrameTransformation)
        if src not in self.transformations:
            self.transformations[src] = {}
        self.transformations[src][dst] = tensor2array(transformation.tf)
        return True
