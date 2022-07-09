import numpy as np

class irradiation_mode():
    def __init__(self, shared_dict):
        pass
        
    def callback(self, param_mause, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        pass
  
    def irradiaion(self, img_display, img_DMD, img_raw,  origin, mapping, size_DMD, shared_dict, q_py2js):
        return img_display, img_DMD
        
    def selected(self, q_py2js):
        pass
        
    def unselected(self, q_py2js):
        pass

    @classmethod
    def declarationSharedmemory(cls):
        return {}

    def changeHTML(cls, q_py2js, Function):
        py2js_dict = {}
        py2js_dict['Function'] = Function
        py2js_dict['repeat'] = 1
        py2js_dict['id'] = "Box_"+ type(cls).__name__
        q_py2js.put(py2js_dict)


class CameraDevice():
    def __init__(self):
        pass

    def change(self):
        pass

    def getframe(self):
        img = np.zeros((1920,1080), dtype= "uint8")
        return img

    def record(self):
        pass
    
    def capture(self):
        pass

    def end(self):
        pass

    @classmethod
    def getnumber(cls):
        list_cam = []
        return list_cam
