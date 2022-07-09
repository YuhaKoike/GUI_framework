from os import name
import cv2
import numpy as np
import PySpin
from decimal import *

#import eel
from script.py.classparents import CameraDevice

def PixelFormat(nodemap):
    node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))
    if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):
        node_pixel_format_BayerRG8 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName('BayerRG8'))

        if PySpin.IsAvailable(node_pixel_format) and PySpin.IsReadable(node_pixel_format):
            pixel_format = node_pixel_format_BayerRG8.GetValue()
            node_pixel_format.SetIntValue(pixel_format)
            print('Pixel format set to %s...' % node_pixel_format.GetCurrentEntry().GetSymbolic())

        else:
            print('Pixel format BayerRG8 not available...')

    else:
        print('Pixel format not available...')

    node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode('OffsetX'))
    if PySpin.IsAvailable(node_offset_x) and PySpin.IsWritable(node_offset_x):

        node_offset_x.SetValue(node_offset_x.GetMin())
        print('Offset X set to %i...' % node_offset_x.GetMin())
        
    else:
        print('Offset X not available...')

    node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode('OffsetY'))
    if PySpin.IsAvailable(node_offset_y) and PySpin.IsWritable(node_offset_y):

        node_offset_y.SetValue(node_offset_y.GetMin())
        print('Offset Y set to %i...' % node_offset_y.GetMin())

    else:
        print('Offset Y not available...')


    node_width = PySpin.CIntegerPtr(nodemap.GetNode('Width'))
    if PySpin.IsAvailable(node_width) and PySpin.IsWritable(node_width):

        width_to_set = node_width.GetMax()
        node_width.SetValue(width_to_set)
        print('Width set to %i...' % node_width.GetValue())
        
    else:
        print('Width not available...')


    node_height = PySpin.CIntegerPtr(nodemap.GetNode('Height'))
    if PySpin.IsAvailable(node_height) and PySpin.IsWritable(node_height):

        height_to_set = node_height.GetMax()
        node_height.SetValue(height_to_set)
        print('Height set to %i...' % node_height.GetValue())

    else:
        print('Height not available...')

    return node_width, node_height

def FrameRateAuto(node_cam, nodemap):
    model = PySpin.CStringPtr(nodemap.GetNode("DeviceModelName")).GetValue()
    # grasshopper
    if "grasshopper" in model or "grasshopper" in model.lower():
        node_acquisition_framerate_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionFrameRateAuto"))
        if PySpin.IsAvailable(node_acquisition_framerate_mode) and PySpin.IsWritable(node_acquisition_framerate_mode):
            node_acquisition_framerate_mode_off = node_acquisition_framerate_mode.GetEntryByName("Off")
            node_acquisition_framerate_mode.SetIntValue(node_acquisition_framerate_mode_off.GetValue())
            node_framerate = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))

    # blackfly
    if "blackfly" in model or "blackfly" in model.lower():
        node_acquisition_framerate = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnable"))
        node_acquisition_framerate.SetValue(True)
        if PySpin.IsAvailable(node_acquisition_framerate) and PySpin.IsWritable(node_acquisition_framerate):
            node_framerate = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))

    if PySpin.IsAvailable(node_framerate) and PySpin.IsReadable(node_framerate):
        node_cam['fps_max'] = decimal_down(node_framerate.GetMax())
        node_cam['fps_min'] = decimal_up(node_framerate.GetMin())
        return node_framerate
    else:
        print('Unable to retrieve frame rate. Aborting...')
        return

def GainAuto(node_cam, nodemap):
    node_gainauto_mode = PySpin.CEnumerationPtr(nodemap.GetNode("GainAuto"))
    if PySpin.IsAvailable(node_gainauto_mode) and PySpin.IsWritable(node_gainauto_mode):
        node_gainauto_mode_off = node_gainauto_mode.GetEntryByName("Off")
        node_gainauto_mode.SetIntValue(node_gainauto_mode_off.GetValue())
        node_gain = PySpin.CFloatPtr(nodemap.GetNode("Gain"))

        if PySpin.IsAvailable(node_gain) and PySpin.IsReadable(node_gain):
            node_cam['gain_max'] = decimal_down(node_gain.GetMax())
            node_cam['gain_min'] = decimal_up(node_gain.GetMin())
            return node_gain
        else:
            print('Unable to retrieve gain. Aborting...')
            return

def ExposureAuto(node_cam, nodemap):
    node_exposureauto_mode = PySpin.CEnumerationPtr(nodemap.GetNode("ExposureAuto"))
    if PySpin.IsAvailable(node_exposureauto_mode) and PySpin.IsWritable(node_exposureauto_mode):
        node_exposureauto_mode_off = node_exposureauto_mode.GetEntryByName("Off")
        node_exposureauto_mode.SetIntValue(node_exposureauto_mode_off.GetValue())
        node_exposure_time = PySpin.CFloatPtr(nodemap.GetNode("ExposureTime"))

        if PySpin.IsAvailable(node_exposure_time) and PySpin.IsReadable(node_exposure_time):
            node_cam['exptime_max'] = decimal_down(node_exposure_time.GetMax() * 0.99)
            node_cam['exptime_min'] = decimal_up(node_exposure_time.GetMin())
            return node_exposure_time
        else:
            print('Unable to retrieve exposure time. Aborting...')
            return

def setup(node_cam, data_cam, nodemap, cam):
    node_width, node_height = PixelFormat(nodemap)
    node_framerate = FrameRateAuto(node_cam, nodemap)
    node_gain = GainAuto(node_cam, nodemap)
    node_exposure_time = ExposureAuto(node_cam, nodemap)

    #Setting of bufffer
    s_node_map = cam.GetTLStreamNodeMap()
    handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
    handling_mode_entry = handling_mode.GetEntryByName('NewestOnly') #Buffer NewestOnly or OldestFirst
    handling_mode.SetIntValue(handling_mode_entry.GetValue())

    #Exception handling
    if node_exposure_time.GetValue() <= node_cam['exptime_min']:
        node_cam['exptime_now'] = node_cam['exptime_min']

    else:
        node_cam['exptime_now'] = decimal_down(node_exposure_time.GetValue() * 0.99)

    #now state
    node_cam['gain_now'] = decimal_down(node_gain.GetValue())
    node_cam['fps_now'] = decimal_down(node_framerate.GetValue())
    data_cam['width'] = node_width.GetValue()
    data_cam['height'] = node_height.GetValue()

    return node_exposure_time, node_gain, node_framerate
    
def decimal_down(value):
    decimal_value = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    return float(decimal_value)

def decimal_up(value):
    decimal_value = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_CEILING)
    return float(decimal_value)


class FLIRCam(CameraDevice):
    def __init__(self,flag, info_cam, data_cam, node_cam):

        self.node_cam = node_cam
        # Select camera and initialize
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        #self.cam = self.cam_list.GetByIndex(info_cam[self.progname])

        for i, cam in enumerate(self.cam_list):
            cam.Init()
            nodemap = cam.GetNodeMap()
            node_device_serial_number = PySpin.CStringPtr(nodemap.GetNode('DeviceSerialNumber')).GetValue()

            if node_device_serial_number == info_cam:
                self.cam = cam
                break

        self.cam.Init()

        nodemap = self.cam.GetNodeMap()
        self.node_exposure_time, self.node_gain, self.node_framerate = setup(self.node_cam, data_cam, nodemap, self.cam)

        # Start acquisition
        self.cam.BeginAcquisition()
        
        while self.node_cam['exptime_now'] <= 0.0 and self.node_cam['fps_now'] <= 0.0 and flag.value:
            continue
        self.changenode = True

    def change(self):
        try:
            if self.changenode:
                if self.node_exposure_time.GetMin() < self.node_cam['exptime_now'] < self.node_exposure_time.GetMax():
                    self.node_exposure_time.SetValue(self.node_cam['exptime_now'])
                else:
                    self.node_cam['exptime_now'] = self.node_exposure_time.GetValue()
                if self.node_gain.GetMin() < self.node_cam['gain_now'] < self.node_gain.GetMax():
                    self.node_gain.SetValue(self.node_cam['gain_now'])
                else:
                    self.node_cam['gain_now'] = self.node_gain.GetValue()
                if self.node_framerate.GetMin() < self.node_cam['fps_now'] < self.node_framerate.GetMax():
                    self.node_framerate.SetValue(self.node_cam['fps_now'])
                else:
                    self.node_cam['fps_now'] = self.node_framerate.GetValue()
        finally:
            self.changenode = not self.changenode

    def getframe(self):

        img = self.cam.GetNextImage()
        rawFrame = img.GetNDArray()

        # Release
        img.Release()
        return rawFrame

    def record(self, frame, q_rec_image):
        q_rec_image.put(frame)

    def capture(self, frame, q_cap_image):
        q_cap_image.put(frame)

    def end(self):
        self.cam.EndAcquisition()    # self.system end
        del self.cam
        self.cam_list.Clear()
        self.system.ReleaseInstance()

    @classmethod
    def getnumber(cls):
        list_info = [] #serial, device

        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        
        if not cam_list.GetSize() == 0:
            list_info = [[0] * 3 for j in range(len(cam_list))]
            for i, cam in enumerate(cam_list):
                cam.Init()
                nodemap = cam.GetNodeMap()
                node_device_serial_number = PySpin.CStringPtr(nodemap.GetNode('DeviceSerialNumber'))
                node_device_model_name  = PySpin.CStringPtr(nodemap.GetNode('DeviceModelName'))

                if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                    list_info[i][0] = node_device_serial_number.GetValue()
                    list_info[i][1] = node_device_model_name.GetValue()

            del cam
        cam_list.Clear()
        system.ReleaseInstance()
        return list_info

params = {'MSEC': 0,
        'POS_FRAMES': 1,
        'POS_AVI_RATIO': 2,
        'FRAME_WIDTH': 3,
        'FRAME_HEIGHT': 4,
        'PROP_FPS' : 5,
        'PROP_FOURCC': 6,
        'FRAME_COUNT': 7,
        'FORMAT': 8,
        'MODE': 9,
        'BRIGHTNESS': 10,
        'CONTRAST': 11,
        'SATURATION': 12,
        'HUE': 13,
        'GAIN': 14,
        'EXPOSURE': 15,
        'CONVERT_RGB': 16,
        'WHITE_BALANCE': 17,
        'RECTIFICATION': 18}

class Webcamera(CameraDevice):

    def __init__(self, flag, info_cam, data_cam, node_cam):
        self.camera = cv2.VideoCapture(0)
        #self.node_cam = node_cam

        node_cam['exptime_now'], node_cam['exptime_max'], node_cam['exptime_min'] = 1, 1, 0
        node_cam['gain_now'], node_cam['gain_max'], node_cam['gain_min'] = 1, 1, 0
        node_cam['fps_now'], node_cam['fps_max'], node_cam['fps_min'] = self.camera.get(params['PROP_FPS']), 1, 1

        data_cam['height'] = int(self.camera.get(params['FRAME_HEIGHT']))
        data_cam['width'] = int(self.camera.get(params['FRAME_WIDTH']))

    def getframe(self):
        ret, rawFrame = self.camera.read()
        return rawFrame

    def record(self, frame, q_rec_image):
        q_rec_image.put(frame)

    def capture(self, frame, q_cap_image):
        q_cap_image.put(frame)

    @classmethod
    def getnumber(cls):
        list_info = [] #serial, device
        serial = 0
        camera = cv2.VideoCapture(serial)

        while camera.isOpened():
            list_info += [[serial, "webcamera"]]
            serial += 1
            camera = cv2.VideoCapture(serial)

        return list_info

class Nonecam(CameraDevice):

    def __init__(self, flag, info_cam, data_cam, node_cam):
        self.rawFrame = np.zeros((1920, 1200), np.uint8)
        self.rawFrame += 100

        node_cam['exptime_now'], node_cam['exptime_max'], node_cam['exptime_min'] = 1, 1, 0
        node_cam['gain_now'], node_cam['gain_max'], node_cam['gain_min'] = 1, 1, 0
        node_cam['fps_now'], node_cam['fps_max'], node_cam['fps_min'] = 1, 1, 0
        
        data_cam['height'] = self.rawFrame.shape[1]
        data_cam['width'] = self.rawFrame.shape[0]

    def record(self, frame, q_rec_image):
        q_rec_image.put(frame)

    def capture(self, frame, q_cap_image):
        q_cap_image.put(frame)

    def getframe(self):
        return self.rawFrame

    pass
