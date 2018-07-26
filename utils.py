import sys
import cv2
import numpy as np
from is_msgs.image_pb2 import Image
from google.protobuf.json_format import Parse
from options_pb2 import SkeletonsHeatmapOptions
from is_wire.core import Logger

def to_pb_image(input_image, encode_format='.jpeg', compression_level=0.8):
    if isinstance(input_image, np.ndarray):
        if encode_format == '.jpeg':
            params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * (100 - 0) + 0)]
        elif encode_format == '.png':
            params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * (9 - 0) + 0)]
        else:
            return Image()
        cimage = cv2.imencode(ext=encode_format, img=input_image, params=params)
        return Image(data=cimage[1].tobytes())
    elif isinstance(input_image, Image):
        return input_image
    else:
        return Image()


def load_options():
    log = Logger()
    op_file = sys.argv[1] if len(sys.argv) > 1 else 'options.json'
    try:
        with open(op_file, 'r') as f:
            try:
                op = Parse(f.read(), SkeletonsHeatmapOptions())
                log.info('Options: \n{}', op)
                return op
            except Exception as ex:
                log.critical(
                    'Unable to load options from \'{}\'. \n{}', op_file, ex)
            except:
                log.critical('Unable to load options from \'{}\'', op_file)
    except Exception as ex:
        log.critical('Unable to open file \'{}\'', op_file)
