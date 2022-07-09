import eel
import glob
import os
import re
from screeninfo import get_monitors

#import userfile.camera as camera
from script.py.classparents import CameraDevice
#import script.py.MakeHTML as MakeHTML
from script.py.classparents import irradiation_mode
#for .irradiation_mode.__subclasses__()
import userfile.irradiation

def count_cam():
    info_cam  = {'num': -1, 'cam1': [-1, 'NoneClassObj'], 'cam2': [-1, 'NoneClassObj'], 'switch': True}

    def onCloseWindow(page, socket):
        info_cam['switch'] = False

    def find_classObj(classname):
        list_CameraDevice = CameraDevice.__subclasses__()
        for class_CameraDevice in list_CameraDevice:
            if class_CameraDevice.__name__ == classname:
                return class_CameraDevice
        return None

    @eel.expose
    def get_num(list):
        if list[1][0] == list[2][0] == -1:
            list[1][1] = "Nonecam"
        info_cam['num'] = list[0]
        info_cam['cam1'] = [list[1][0], find_classObj(list[1][1])]
        info_cam['cam2'] = [list[2][0], find_classObj(list[2][1])]

    @eel.expose
    def py_camlist():
        list_CameraDevice = CameraDevice.__subclasses__()
        list_info = {}
        for ins_CameraDevice in list_CameraDevice:
            list_info[ins_CameraDevice.__name__] = ins_CameraDevice.getnumber()
        eel.js_camlist(list_info)

    eel.init('script')
    eel.start("html/select_cam.html", size=(600, 500), position=(960, 0), close_callback=onCloseWindow, block=False, port=8001)
    
    while info_cam['switch']:
        eel.sleep(1)
    
    return info_cam

def irradiationHTML():
    def makeelement(htmllist, elem, dic):
        text = '###' + elem
        p = text + r'\n' + '((.|\s)*?)' + r'\n' + text
        html = re.findall(p, htmllist)[0][0]
        for key, value in dic.items():
            html = html.replace('{% '+key+' %}', value)
        return html + '\n'

    htmlmain = ""

    list_modeclass = irradiation_mode.__subclasses__()

    shared_dict = {'Mode': list_modeclass[0].__name__, 'Monitor': None, 'calibrationStart': False, "calib_pass": False, 'calib_x0': 0, 'calib_x1': 0, 'calib_y0': 0, 'calib_y1': 0}
    for modeclass in list_modeclass:
        shared_dict = {**shared_dict,**modeclass.declarationSharedmemory()}

    #html list open
    path_html = "script/html/UI.html"
    if os.path.exists(path_html):
        with open(path_html)as f:
            htmllist = f.read()
            #Monitor
            dic = {}
            options = ''
            for monitor in get_monitors():
                name = re.sub(r"[^a-zA-Z0-9]", "", monitor.name)
                dic['ID'] = name
                dic['VALUE'] = name
                dic['NAME'] = name
                if monitor.x == 1920:
                    dic['SELECTED'] = 'selected'
                else:
                    dic['SELECTED'] = ''

                options += makeelement(htmllist, 'option', dic)

            dic = {'OPTIONS': options}
            htmlmain += makeelement(htmllist, 'monitorselect', dic)
            htmlmain += "</br>"

            #Mode
            dic = {}
            options = ''
            for modeclass in list_modeclass:
                dic['ID'] = modeclass.__name__
                dic['VALUE'] = modeclass.__name__
                dic['NAME'] = modeclass.__name__
                dic['SELECTED'] = ''
                options += makeelement(htmllist, 'option', dic)
            dic = {'OPTIONS': options}
            htmlmain += makeelement(htmllist, 'modeselect', dic)

            #Control
            dic = {}
            contents = ''
            for i, modeclass in enumerate(list_modeclass):
                dic = {'CONTENTS': ''}
                if i == 0:
                    dic['ID'] = "Box_"+ modeclass.__name__
                    dic['STYLE'] = ""
                else:
                    dic['ID'] = "Box_"+ modeclass.__name__
                    dic['STYLE'] = "display: none"

                path_html = "./userfile/InputValue/"+modeclass.__name__+".html"
                if os.path.exists(path_html):
                    value_dict = modeclass.declarationSharedmemory()
                    with open(path_html)as f:
                        html = f.read()
                    for key, value in value_dict.items():
                        html = html.replace('{% id:' + key + ' %}', "\'" + key + "\'")
                        html = html.replace('{% value:' + key + ' %}', "\'" + str(value) + "\'")
                        html = html.replace('{% JS:' + key + ' %}', "\'" + 'js2py(this.value,"'+key+'")' + "\'")
                    dic['CONTENTS'] = html
                contents += makeelement(htmllist, 'div', dic)
            dic = {'ID': 'Box_Control', 'STYLE': '', 'CONTENTS': contents}
            htmlmain += makeelement(htmllist, 'div', dic)

    return htmlmain, shared_dict

def htmlfile(page_data):
    folder = 'script/'
    file = glob.glob(folder+'/html/index.html')
    if not file == []:
        os.remove(folder+'/html/index.html')

    #cgitb.enable()
    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    #read html file
    with open(folder + '/html/base.html','r') as file:
        html = file.read()
    file.closed

    #change {% %} to page_data
    for key, value in page_data.items():
        html = html.replace('{% ' + key + ' %}', value)

    #output html
    with open(folder + '/html/index.html', 'w', encoding='utf-8') as file:
        file.write(html)
    file.closed


def HTMLinit():
    htmlmain, shared_dict = irradiationHTML()
    page_data = {'main': htmlmain, 'page_title': "Test"}
    htmlfile(page_data)

    return  shared_dict