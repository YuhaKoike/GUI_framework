import numpy as np
import cv2

import userfile.camera as camera
from script.py.classparents import CameraDevice

# 名前変えたい
def cam1(flag, progname, info_cam, q_byte_image, q_rec_image, q_cap_image, data_cam, node_cam, record):
    camIns = info_cam[1](flag, info_cam[0], data_cam, node_cam,)

    while flag.value:
        if record['mode'] == 0:
            camIns.change()
        rawFrame = camIns.getframe()
        if q_byte_image.empty():
            q_byte_image.put(rawFrame)

        if record['mode'] == 1:
            camIns.record(rawFrame, q_rec_image)
            record['framenum'] += 1

        if record['capture'] == 1 and q_cap_image.empty():
            camIns.capture(rawFrame, q_cap_image)
            record['capture'] = 2
        #RecCap(rawFrame, progname, record, q_rec_image, q_cap_image)

    camIns.end()
