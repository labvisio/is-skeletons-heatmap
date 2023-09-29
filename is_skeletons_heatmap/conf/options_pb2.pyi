from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor
NONE: RotateFlags
ROTATE_180: RotateFlags
ROTATE_90_CCW: RotateFlags
ROTATE_90_CW: RotateFlags

class AreaLimits(_message.Message):
    __slots__ = ["xmax", "xmin", "ymax", "ymin"]
    XMAX_FIELD_NUMBER: ClassVar[int]
    XMIN_FIELD_NUMBER: ClassVar[int]
    YMAX_FIELD_NUMBER: ClassVar[int]
    YMIN_FIELD_NUMBER: ClassVar[int]
    xmax: float
    xmin: float
    ymax: float
    ymin: float
    def __init__(self, xmin: Optional[float] = ..., xmax: Optional[float] = ..., ymin: Optional[float] = ..., ymax: Optional[float] = ...) -> None: ...

class ReferentialProperties(_message.Message):
    __slots__ = ["length", "x", "y"]
    LENGTH_FIELD_NUMBER: ClassVar[int]
    X_FIELD_NUMBER: ClassVar[int]
    Y_FIELD_NUMBER: ClassVar[int]
    length: int
    x: float
    y: float
    def __init__(self, x: Optional[float] = ..., y: Optional[float] = ..., length: Optional[int] = ...) -> None: ...

class SkeletonsHeatmapOptions(_message.Message):
    __slots__ = ["average_coordinates", "bins_step", "broker_uri", "draw_grid", "flip_horizontal", "flip_vertical", "frame_id", "group_ids", "limits", "log_scale", "output_rotate", "output_scale", "period_ms", "referential", "samples", "zipkin_host", "zipkin_port"]
    AVERAGE_COORDINATES_FIELD_NUMBER: ClassVar[int]
    BINS_STEP_FIELD_NUMBER: ClassVar[int]
    BROKER_URI_FIELD_NUMBER: ClassVar[int]
    DRAW_GRID_FIELD_NUMBER: ClassVar[int]
    FLIP_HORIZONTAL_FIELD_NUMBER: ClassVar[int]
    FLIP_VERTICAL_FIELD_NUMBER: ClassVar[int]
    FRAME_ID_FIELD_NUMBER: ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: ClassVar[int]
    LIMITS_FIELD_NUMBER: ClassVar[int]
    LOG_SCALE_FIELD_NUMBER: ClassVar[int]
    OUTPUT_ROTATE_FIELD_NUMBER: ClassVar[int]
    OUTPUT_SCALE_FIELD_NUMBER: ClassVar[int]
    PERIOD_MS_FIELD_NUMBER: ClassVar[int]
    REFERENTIAL_FIELD_NUMBER: ClassVar[int]
    SAMPLES_FIELD_NUMBER: ClassVar[int]
    ZIPKIN_HOST_FIELD_NUMBER: ClassVar[int]
    ZIPKIN_PORT_FIELD_NUMBER: ClassVar[int]
    average_coordinates: bool
    bins_step: float
    broker_uri: str
    draw_grid: bool
    flip_horizontal: bool
    flip_vertical: bool
    frame_id: int
    group_ids: _containers.RepeatedScalarFieldContainer[int]
    limits: AreaLimits
    log_scale: bool
    output_rotate: RotateFlags
    output_scale: _wrappers_pb2.FloatValue
    period_ms: int
    referential: ReferentialProperties
    samples: int
    zipkin_host: str
    zipkin_port: int
    def __init__(self, broker_uri: Optional[str] = ..., zipkin_host: Optional[str] = ..., zipkin_port: Optional[int] = ..., group_ids: Optional[Iterable[int]] = ..., limits: Optional[Union[AreaLimits, Mapping]] = ..., bins_step: Optional[float] = ..., output_scale: Optional[Union[_wrappers_pb2.FloatValue, Mapping]] = ..., output_rotate: Optional[Union[RotateFlags, str]] = ..., frame_id: Optional[int] = ..., referential: Optional[Union[ReferentialProperties, Mapping]] = ..., draw_grid: bool = ..., flip_horizontal: bool = ..., flip_vertical: bool = ..., log_scale: bool = ..., average_coordinates: bool = ..., samples: Optional[int] = ..., period_ms: Optional[int] = ...) -> None: ...

class RotateFlags(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
