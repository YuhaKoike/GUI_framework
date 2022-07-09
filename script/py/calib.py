import cv2
import numpy as np

from script.py.classparents import irradiation_mode

#class calib_mode(irradiation_mode):
class calib_mode():
    def __init__(self, shared_dict):
        self.calib_step = 0
        self.calib_size = 20
        pass
        
    def callback(self, param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):

        if param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            if self.calib_step == 0 :
                origin[:] = (param_mause['x'], param_mause['y'])
                shared_dict['calib_x0'], shared_dict['calib_y0'] = param_mause['x'], param_mause['y']
            if self.calib_step == 1 :
                mapping[0] = size_DMD[0]/(param_mause['x'] -origin[0])
                shared_dict['calib_x1'] = param_mause['x']
            if self.calib_step == 2 :
                mapping[1] = size_DMD[1]/(param_mause['y'] -origin[1])
                shared_dict['calib_y1'] = param_mause['y']
            
            self.calib_step += 1

    def irradiaion(self, img_display, img_DMD, img_raw, size_DMD, shared_dict, q_py2js):
        if self.calib_step == 0 :
            #img_DMD = drow_dmd(img_DMD, (0,0), (self.calib_size, self.calib_size))
            cv2.rectangle(img_DMD, (0,0), (self.calib_size, self.calib_size), (1, 1, 1), thickness = -1)
        elif self.calib_step == 1 :
            #img_DMD = drow_dmd(img_DMD, (size_DMD[0].astype(np.int) - self.calib_size, 0), (size_DMD[0].astype(np.int), self.calib_size))
            cv2.rectangle(img_DMD, (size_DMD[0].astype(np.int) - self.calib_size, 0), (size_DMD[0].astype(np.int), self.calib_size), (1, 1, 1), thickness = -1)
        elif self.calib_step == 2 :
            #img_DMD = drow_dmd(img_DMD, (0,size_DMD[1].astype(np.int) - self.calib_size), (self.calib_size, size_DMD[0].astype(np.int)))
            cv2.rectangle(img_DMD,(0,size_DMD[1].astype(np.int) - self.calib_size), (self.calib_size, size_DMD[0].astype(np.int)), (1, 1, 1), thickness = -1)

        calib_end = False
        if self.calib_step == 3 :
            self.calib_step = 0
            calib_end = True

        return img_display, img_DMD, calib_end

