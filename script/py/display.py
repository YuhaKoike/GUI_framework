import cv2
import numpy as np
from multiprocessing import Process, Manager, Value, Queue
from screeninfo import get_monitors

import sys
import re

from screeninfo.screeninfo import get_monitors
sys.path.append('./')
from script.py.classparents import irradiation_mode
#for .irradiation_mode.__subclasses__()
import userfile.irradiation
from script.py.calib import calib_mode

def callback(event, x, y, flags, param):
    param_callback = {'event':event, 'x':x, 'y':y, 'flags':flags,}
    param["queue_callback"].put(param_callback)

def Display(flag, shared_dict, q_py2js, n_cam, q_byte_image1, q_byte_image2, data_cam, node_cam):
    camlist = ['cam1', 'cam2']
    byte_image = {'cam1': q_byte_image1, 'cam2': q_byte_image2}

    while True:
        if n_cam < 2:
            if data_cam['cam1']['width'] > 0 and data_cam['cam1']['height'] > 0:
                break
        else:
            if data_cam['cam1']['width'] > 0 and data_cam['cam1']['height'] > 0 and data_cam['cam2']['width'] > 0 and data_cam['cam2']['height'] > 0:
                break

        if flag.value == False:
            break

    size_DMD = np.array((1280.0,800.0)) #x, y
    origin = np.array((0,0)) #x, y
    mapping = np.array((1.0,1.0)) #x,y DMD/input
    scale = 50/100
    queue_callback = Queue()
    param_callback = {'queue_callback' : queue_callback}
    param_mause = {'event':-1, 'x':-1, 'y':-1, 'flags':0,}

    window_input_name = ['Bottom', 'Side']
    window_input = {'cam1': 'Bottom'}
    for i in range(n_cam):
        window_input[camlist[i]] = window_input_name[i]

    for key, val in window_input.items():
        cv2.namedWindow(window_input[key], cv2.WINDOW_AUTOSIZE)
        if key == 'cam1':
            cv2.moveWindow(window_input[key], 0, 0)
            cv2.setMouseCallback(window_input[key], callback, param_callback)
        else:
            cv2.moveWindow(window_input[key], 0, 540)

    window_DMD = 'DMD'
    #cv2.namedWindow(window_DMD, cv2.WND_PROP_FULLSCREEN)
    cv2.namedWindow(window_DMD, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_DMD, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    nowmonitor = None
    cv2.moveWindow(window_DMD, 1920, 0)

    calib = calib_mode(shared_dict)

    list_modeclass = irradiation_mode.__subclasses__()
    list_modeinstance = [i(shared_dict) for i in list_modeclass]
    num_instance = 0
    list_modeinstance[num_instance].changeHTML(q_py2js, "Show")
    img_raw = np.zeros((data_cam['cam1']['width'], data_cam['cam1']['height']), np.uint8)
    resize = (int(scale*data_cam['cam1']['width']), int(scale*data_cam['cam1']['height']))
    img_display = img_raw.copy()

    while flag.value:
        if not byte_image['cam1'].empty():
            img_raw = byte_image['cam1'].get()
            img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BAYER_BG2BGR)
            if not data_cam['cam1']['color']:
                if len(img_raw.shape[:]) != 2:
                    if img_raw.shape[2] == 3:
                        img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)

            resize = (int(scale*data_cam['cam1']['width']), int(scale*data_cam['cam1']['height']))

        img_display = cv2.resize(img_raw, resize, interpolation = cv2.INTER_LINEAR)

        img_DMD = np.zeros((int(size_DMD[1]), int(size_DMD[0]),3),dtype = np.uint8)
        
        #calibration mode
        if shared_dict['calibrationStart'] == True:

            while not param_callback["queue_callback"].empty():
                param_mause = param_callback["queue_callback"].get_nowait()
                calib.callback(param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js)
            img_display, img_DMD, calib_end = calib.irradiaion(img_display, img_DMD, img_raw,  size_DMD, shared_dict, q_py2js)

            if calib_end == True:
                shared_dict['calibrationStart'] = False
                shared_dict["calib_pass"] = True

        #irradiation mode
        else :
            if not shared_dict["calibrationStart"]:
                origin[:] = (shared_dict["calib_x0"], shared_dict["calib_y0"])
                mapping[:] = (size_DMD[0]/(shared_dict["calib_x1"] -origin[0]), size_DMD[1]/(shared_dict["calib_y1"] -origin[1]))

            #drow irradiation area
            cv2.rectangle(img_display, tuple(map(int,(shared_dict['calib_x0'], shared_dict['calib_y0']))), tuple(map(int, (shared_dict['calib_x1'], shared_dict['calib_y1']))), (255, 255, 255), 1)
            
            #drow position
            cv2.putText(img_display, 'x0, y0', tuple(map(int, (shared_dict['calib_x0'], shared_dict['calib_y0']))), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
            cv2.putText(img_display, 'x1, y1', tuple(map(int, (shared_dict['calib_x1'], shared_dict['calib_y1']))), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

            for i, instance in enumerate(list_modeinstance):
                if shared_dict['Mode'] == instance.__class__.__name__:
                    if num_instance != i:
                        list_modeinstance[num_instance].unselected(q_py2js)
                        list_modeinstance[num_instance].changeHTML(q_py2js, "Hide")
                        num_instance = i
                        list_modeinstance[num_instance].changeHTML(q_py2js, "Show")
                        list_modeinstance[num_instance].selected(q_py2js)
                        break
            
            while not param_callback["queue_callback"].empty():
                param_mause = param_callback["queue_callback"].get_nowait()
                list_modeinstance[num_instance].callback(param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js)
            img_display, img_DMD = list_modeinstance[num_instance].irradiaion(img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js)


        cv2.imshow(window_input['cam1'], img_display)
        img_DMD = img_DMD * 253 + 1
        if not nowmonitor == shared_dict['Monitor']:
            for monitor in get_monitors():
                if shared_dict['Monitor'] in monitor.name.upper():
                    nowmonitor = re.sub(r"[^a-zA-Z0-9]", "", monitor.name)
                    cv2.moveWindow(window_DMD, monitor.x, monitor.y)

        cv2.imshow(window_DMD, img_DMD)

        if n_cam == 2:
            if not byte_image['cam2'].empty():
                image_side = byte_image['cam2'].get()
                resize_cam2 = (int(scale*data_cam['cam2']['width']), int(scale*data_cam['cam2']['height']))
                img_display_side= cv2.resize(image_side, resize_cam2, interpolation = cv2.INTER_LINEAR)
                cv2.imshow(window_input['cam2'], img_display_side)

        cv2.waitKey(1)

    cv2.destroyAllWindows()
