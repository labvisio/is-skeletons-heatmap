from typing import Any

import cv2
import numpy as np
import numpy.typing as npt
from is_msgs.common_pb2 import DataType, Tensor
from is_msgs.image_pb2 import Image, Vertex


def array2image(
    input_image: npt.NDArray[np.uint8],
    encode_format: str = ".jpeg",
    compression_level: float = 0.8,
) -> Image:
    if encode_format == ".jpeg":
        params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * (100 - 0) + 0)]
    elif encode_format == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * (9 - 0) + 0)]
    else:
        return Image()
    cimage = cv2.imencode(ext=encode_format, img=input_image, params=params)
    return Image(data=cimage[1].tobytes())


def tensor2array(tensor: Tensor) -> npt.NDArray[Any]:
    if len(tensor.shape.dims) != 2 or tensor.shape.dims[0].name != "rows":
        return np.array([])
    shape = (tensor.shape.dims[0].size, tensor.shape.dims[1].size)
    if tensor.type == DataType.Value("INT32_TYPE"):
        return np.array(tensor.ints32, dtype=np.int32, copy=False).reshape(shape)
    if tensor.type == DataType.Value("INT64_TYPE"):
        return np.array(tensor.ints64, dtype=np.int64, copy=False).reshape(shape)
    if tensor.type == DataType.Value("FLOAT_TYPE"):
        return np.array(tensor.floats, dtype=np.float32, copy=False).reshape(shape)
    if tensor.type == DataType.Value("DOUBLE_TYPE"):
        return np.array(tensor.doubles, dtype=np.float64, copy=False).reshape(shape)
    return np.array([])


def vertex2array(vertex: Vertex, homogeneous: bool = False) -> npt.NDArray[np.float32]:
    if homogeneous:
        return np.array([vertex.x, vertex.y, vertex.z, 1.0])
    return np.array([vertex.x, vertex.y, vertex.z])


def array2vertex(vertex: npt.NDArray[np.float32]) -> Vertex:
    return Vertex(x=vertex[0], y=vertex[1], z=vertex[2])
