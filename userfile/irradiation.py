import cv2
import numpy as np
from script.py.classparents import irradiation_mode

class Grid(irradiation_mode):
    def __init__(self, shared_dict):
        self.grid_num_v = 10
        self.grid_num_h = 10
        self.grid_irradiation = np.zeros((10,10))
        self.grid_area =  np.array((640.0,400.0))#x, y
        self.grid_area_origin = np.array((100.0,100.0))#x, y
        self.box = self.grid_area/[self.grid_num_v,self.grid_num_h]
        self.setupbox = False
        
    def callback(self, param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        if param_mause['event'] == cv2.EVENT_MOUSEMOVE and param_mause['flags'] == cv2.EVENT_FLAG_LBUTTON:
            if not shared_dict['setupgrid']:
                self.grid_x = ((param_mause['x']-self.grid_area_origin[0])/self.box[0]).astype(np.int)
                self.grid_y = ((param_mause['y']-self.grid_area_origin[1])/self.box[1]).astype(np.int)
                if 0 <= self.grid_x < self.grid_num_v and 0 <= self.grid_y < self.grid_num_h:
                    self.grid_irradiation[self.grid_x ,self.grid_y] = 1

        elif param_mause['event'] == cv2.EVENT_MOUSEMOVE and param_mause['flags'] == cv2.EVENT_FLAG_RBUTTON:
            if not shared_dict['setupgrid']:
                self.grid_x = ((param_mause['x']-self.grid_area_origin[0])/self.box[0]).astype(np.int)
                self.grid_y = ((param_mause['y']-self.grid_area_origin[1])/self.box[1]).astype(np.int)
                if 0 <= self.grid_x < self.grid_num_v and 0 <= self.grid_y < self.grid_num_h:
                    self.grid_irradiation[self.grid_x ,self.grid_y] = 0

        elif param_mause['event'] == cv2.EVENT_RBUTTONDBLCLK:
            self.grid_irradiation = np.zeros((self.grid_num_v,self.grid_num_h))

        elif param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            if shared_dict['setupgrid']:
                if not self.setupbox:
                    self.grid_area_origin = np.array((param_mause['x'],param_mause['y']))
                    self.box = self.grid_area/[self.grid_num_v,self.grid_num_h ]
                    self.setupbox = True
                else:
                    self.grid_area = np.array((param_mause['x'],param_mause['y'])) - self.grid_area_origin
                    self.box = self.grid_area/[self.grid_num_v,self.grid_num_h ]
                    self.setupbox = False                             

    def irradiaion(self, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        if self.grid_num_h !=  int(shared_dict['grid_num_h']) or self.grid_num_v  != int(shared_dict['grid_num_v']):
            self.grid_num_h = int(shared_dict['grid_num_h'])
            self.grid_num_v = int(shared_dict['grid_num_v'])
            self.grid_irradiation = np.zeros((self.grid_num_v,self.grid_num_h))

        self.box = self.grid_area/[self.grid_num_v,self.grid_num_h ] 

        cv2.rectangle(img_display, tuple((self.grid_area_origin).astype(np.int)), tuple((self.grid_area_origin+self.grid_area).astype(np.int)), (255, 255, 255), 1)

        for i in range(self.grid_num_h-1):
            self.plot_h =  ( self.grid_area_origin[1] + self.box[1]*(i+1) ).astype(np.int)
            img_display = cv2.line(img_display, (self.grid_area_origin[0].astype(np.int),self.plot_h),((self.grid_area_origin+self.grid_area)[0].astype(np.int),self.plot_h),(0,255,0),1)

        for i in range(self.grid_num_v-1):
            self.plot_v =  ( self.grid_area_origin[0] + self.box[0]*(i+1) ).astype(np.int)
            img_display = cv2.line(img_display, (self.plot_v,self.grid_area_origin[1].astype(np.int)),(self.plot_v,(self.grid_area_origin+self.grid_area)[1].astype(np.int)),(0,255,0),1)

        for i in range(self.grid_num_v):
            for j in range(self.grid_num_h):
                if self.grid_irradiation[i,j] == 1:
                    self.pt1 = self.grid_area_origin+self.box*(i,j)
                    self.pt2 = self.grid_area_origin+self.box*(i+1,j+1)
                    cv2.rectangle(img_display, tuple(self.pt1.astype(np.int)), tuple(self.pt2.astype(np.int)), (255, 255, 255), 1)
                    cv2.rectangle(img_DMD, tuple(( ((self.pt1-origin))*mapping ).astype(np.int)), tuple(( ((self.pt2-origin))*mapping ).astype(np.int)), (1, 1, 1), thickness = -1)

        return img_display, img_DMD

    @classmethod
    def declarationSharedmemory(cls):
        sharedmemory = {'grid_num_v':10, 'grid_num_h':10, 'setupgrid': False}
        return sharedmemory

class FullScreen(irradiation_mode):
    def irradiaion(self, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        cv2.rectangle(img_DMD, tuple((0, 0)), tuple(size_DMD.astype(np.int)), (1, 1, 1), thickness = -1)
        return img_display, img_DMD

class Square(irradiation_mode):
    def __init__(self, shared_dict):
        self.Square_pt = np.empty([0,2])

    def callback(self, param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        if param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            self.Square_pt  = np.vstack([self.Square_pt, (param_mause['x'], param_mause['y'])])
            print(self.Square_pt)

        elif param_mause['event'] == cv2.EVENT_RBUTTONDOWN:
            if len(self.Square_pt) >= 2:
                for i in range(int(len(self.Square_pt)/2)):
                    x_min = min(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                    x_max = max(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                    y_min = min(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])
                    y_max = max(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])

                    if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                        self.Square_pt = np.delete(self.Square_pt, [2*i,2*i+1],0)
                        break

        elif param_mause['event'] == cv2.EVENT_RBUTTONDBLCLK:
            self.Square_pt = np.empty([0,2])

    def irradiaion(self, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        if len(self.Square_pt)%2 == 1:
            cv2.drawMarker(img_display, tuple(self.Square_pt[-1].astype(np.int)), (255, 255, 255), markerType = cv2.MARKER_TILTED_CROSS, markerSize=15)

        if len(self.Square_pt) >= 2:
            for i in range(int(len(self.Square_pt)/2)):
                cv2.rectangle(img_display, tuple(self.Square_pt[2*i].astype(np.int)), tuple(self.Square_pt[2*i+1].astype(np.int)), (255, 255, 255), 1)
                cv2.rectangle(img_DMD, tuple(((self.Square_pt[2*i]-origin)*mapping).astype(np.int)), tuple(((self.Square_pt[2*i+1]-origin)*mapping).astype(np.int)), (1, 1, 1), thickness = -1)
        return img_display, img_DMD

class MultiPoints(irradiation_mode):
    def __init__(self, shared_dict):
        self.Square_pt = np.empty([0,3], dtype=object)
        self.mouseposition = np.empty([0,2])

    def callback(self, param_mause, img_display, img_DMD, img_raw, origin, mapping, size_DMD, shared_dict, q_py2js):
        if param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            if shared_dict['setuppoints'] == True:
                try:
                    if not (self.Square_pt[-1][1] == np.array([-1,-1])).all():
                        self.Square_pt = np.vstack([self.Square_pt, (np.array([param_mause['x'], param_mause['y']]), np.array([-1,-1]), False)])
                    else:
                        self.Square_pt[-1][1] = np.array([param_mause['x'], param_mause['y']])
                except:
                    self.Square_pt = np.vstack([self.Square_pt, (np.array([param_mause['x'], param_mause['y']]), np.array([-1,-1]), False)])

            else:
                for pt in self.Square_pt:
                    x_min, x_max = min(pt[0][0], pt[1][0]), max(pt[0][0], pt[1][0])
                    y_min, y_max = min(pt[0][1], pt[1][1]), max(pt[0][1], pt[1][1])
                    if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                        pt[2] = True
                        break

        elif param_mause['event'] == cv2.EVENT_RBUTTONDOWN:
            if shared_dict['setuppoints'] == True:
                for i, pt in enumerate(self.Square_pt):
                    x_min, x_max = min(pt[0][0], pt[1][0]), max(pt[0][0], pt[1][0])
                    y_min, y_max = min(pt[0][1], pt[1][1]), max(pt[0][1], pt[1][1])
                    if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                        self.Square_pt = np.delete(self.Square_pt, [i], 0)
                        break
            else:
                for pt in self.Square_pt:
                    x_min, x_max = min(pt[0][0], pt[1][0]), max(pt[0][0], pt[1][0])
                    y_min, y_max = min(pt[0][1], pt[1][1]), max(pt[0][1], pt[1][1])
                    if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                        pt[2] = False
                        break

        elif param_mause['event'] == cv2.EVENT_MOUSEMOVE:
            self.mouseposition = np.array([param_mause['x'], param_mause['y']])

        elif param_mause['event'] == cv2.EVENT_RBUTTONDBLCLK:
            if shared_dict['setuppoints'] == True:
                self.Square_pt = np.empty([0,3], dtype=object)
            else:
                for pt in self.Square_pt:
                    pt[2] = False

    def irradiaion(self, img_display, img_DMD, img_raw, origin, mapping, size_DMD, shared_dict, q_py2js):
        for pt in self.Square_pt:
            if (pt[1] == np.array([-1,-1])).all():
                cv2.rectangle(img_display, tuple(pt[0].astype(np.int)), tuple(self.mouseposition.astype(np.int)), (255,255,255), 1)
            else:
                cv2.rectangle(img_display, tuple(pt[0].astype(np.int)), tuple(pt[1].astype(np.int)), (255,255,255), 1)
                if pt[2] == True:
                    cv2.rectangle(img_DMD, tuple(((pt[0]-origin)*mapping).astype(np.int)), tuple(((pt[1]-origin)*mapping).astype(np.int)), (1, 1, 1), thickness=-1)

        return img_display, img_DMD

    @classmethod
    def declarationSharedmemory(cls):
        sharedmemory = {'setuppoints': True}
        return sharedmemory

class Sample(irradiation_mode):
    def __init__(self, shared_dict):
        self.py2js_dict = {}
        self.sample_count = np.empty([0,3], int)
        self.count_id = 0

    def irradiaion(self, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        for i, pt in enumerate(self.sample_count):
            pt[0] = shared_dict[str(self.count_id - len(self.sample_count) + i) + "_x"]
            pt[1] = shared_dict[str(self.count_id - len(self.sample_count) + i) + "_y"]
            cv2.drawMarker(img_display, tuple(pt[:2]), (255, 255, 255), markerType = cv2.MARKER_TILTED_CROSS, markerSize=15)
        
        return img_display, img_DMD

    def callback(self, param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        if param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            self.sample_count = np.vstack([self.sample_count, (param_mause['x'], param_mause['y'], self.count_id)])

            self.py2js_dict = {}
            self.py2js_dict['Function'] = "Create"
            self.py2js_dict['tagName'] = ["text", "input", "text", "input"]
            self.py2js_dict['id'] = ["text_" + str(self.count_id) + "_x", str(self.count_id) + "_x", "text_" + str(self.count_id) + "_y", str(self.count_id) + "_y"]
            self.py2js_dict['parentid'] = "Box_Sample"
            self.py2js_dict['val'] = ["x", self.sample_count[len(self.sample_count) - 1][0], "y", self.sample_count[len(self.sample_count) - 1][1]]
            self.py2js_dict['repeat'] = 4
            shared_dict[str(self.count_id) + "_x"] = self.sample_count[len(self.sample_count) - 1][0]
            shared_dict[str(self.count_id) + "_y"] = self.sample_count[len(self.sample_count) - 1][1]
            self.count_id += 1
            q_py2js.put(self.py2js_dict)

        elif param_mause['event'] == cv2.EVENT_RBUTTONDOWN and not len(self.sample_count) == 0:
            self.py2js_dict = {}
            self.py2js_dict['Function'] = "Delete"
            self.py2js_dict['id'] = ["text_" + str(self.count_id - len(self.sample_count)) + "_x", str(self.count_id - len(self.sample_count)) + "_x", "text_" + str(self.count_id - len(self.sample_count)) + "_y", str(self.count_id - len(self.sample_count)) + "_y"]
            self.py2js_dict['repeat'] = 4
            q_py2js.put(self.py2js_dict)

            shared_dict.pop(str(self.count_id - len(self.sample_count)) + "_x")
            shared_dict.pop(str(self.count_id - len(self.sample_count)) + "_y")

            self.sample_count = np.delete(self.sample_count, 0, 0)

    def unselected(self, q_py2js):
        for pt in self.sample_count:
            self.py2js_dict = {}
            self.py2js_dict['Function'] = "Delete"
            self.py2js_dict['id'] = ["text_" + str(pt[2]) + "_x", str(pt[2]) + "_x", "text_" + str(pt[2]) + "_y", str(pt[2]) + "_y"]
            self.py2js_dict['repeat'] = 4
            q_py2js.put(self.py2js_dict)

        self.sample_count = np.empty([0,3], int)
        self.count_id = 0

class Sample2(irradiation_mode):
    def __init__(self,shared_dict):
        self.Square_pt = np.empty([0,2])
        self.irradiation_pt = np.empty([0,2])

    def callback(self, param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        if param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            self.Square_pt  = np.vstack([self.Square_pt, (param_mause['x'], param_mause['y'])])

        elif param_mause['event'] == cv2.EVENT_MBUTTONDOWN:
            if len(self.Square_pt) >= 2:
                for i in range(int(len(self.Square_pt)/2)):
                        x_min = min(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                        x_max = max(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                        y_min = min(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])
                        y_max = max(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])
                            
                        if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                            self.irradiation_pt  = np.vstack([self.irradiation_pt, (param_mause['x'], param_mause['y'])])
                            break

        elif param_mause['event'] == cv2.EVENT_RBUTTONDOWN:
            if len(self.Square_pt) >= 2 and len(self.irradiation_pt) >= 1:
                for i in range(int(len(self.Square_pt)/2)):
                    x_min = min(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                    x_max = max(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                    y_min = min(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])
                    y_max = max(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])
                        
                    if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                        for j in range(int(len(self.irradiation_pt))):
                            if x_min < (self.irradiation_pt[j][0]) < x_max and y_min < (self.irradiation_pt[j][1]) < y_max: 
                                self.irradiation_pt = np.delete(self.irradiation_pt, [j],0)
                                break
                                    
        elif param_mause['event'] == cv2.EVENT_RBUTTONDBLCLK:
            if len(self.Square_pt) >= 2:
                for i in range(int(len(self.Square_pt)/2)):
                    x_min = min(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                    x_max = max(self.Square_pt[2*i][0], self.Square_pt[2*i+1][0])
                    y_min = min(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])
                    y_max = max(self.Square_pt[2*i][1], self.Square_pt[2*i+1][1])

                    if x_min < param_mause['x'] < x_max and y_min < param_mause['y'] < y_max:
                        self.Square_pt = np.delete(self.Square_pt, [2*i,2*i+1],0)
                        break

class frecpattern(irradiation_mode):
    def __init__(self,shared_dict):
        self.irradiation_areas = np.empty([0, 2], dtype=object)
        pass

    def callback(self, param_mause, img_display, img_DMD, img_raw, origin, mapping, size_DMD, shared_dict, q_py2js):
        if param_mause['event'] == cv2.EVENT_LBUTTONDOWN:
            print(self.irradiation_areas)

    def irradiaion(self, img_display, img_DMD, img_raw, origin, mapping, size_DMD, shared_dict, q_py2js):
        return img_display, img_DMD