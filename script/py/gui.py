import os
import eel
import time
import datetime
import numpy as np
import tkinter
from tkinter import filedialog
import json

def GuiMenu(flag, q_log, shared_dict, node_cam, data_cam, n_cam, record, q_py2js):

    py2js_dict = {}
    py2js_dict = q_py2js.get()

    camname = ['cam1',]
    for i in range(n_cam):
        try:
            camname[i] = 'cam' + str(i + 1)
        except:
            camname.append('cam' + str(i + 1))

    def onCloseWindow(page, _):
        flag.value = False
        print(page + ' end')

    #"""
    @eel.expose
    def SelectSaveFolder(id):
        root = tkinter.Tk()
        #root.withdraw()
        fTyp = [('AVI', '.avi')]
        iDir = 'C:\\'
        now = datetime.datetime.now()
        iFile = now.strftime('%Y%m%d_%H%M%S')
        #iFile = ''
        file = filedialog.asksaveasfilename(filetypes = fTyp, initialdir = iDir, initialfile = iFile)

        root.destroy()
        if not file == '':
            for cam in camname:
                record[cam]['folder'] = file
                record[cam]['filename'] = iFile
 
            eel.jsChangeValue(id, file)

    @eel.expose
    def roi(id):
        root = tkinter.Tk()
        fTyp = [('json file', '.json')]
        iDir = 'C:\\'
        
        iFile = ''
        if 'Input' in id:
            filename = filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir, initialfile = iFile)

            if not filename == "":
                with open(filename) as f:
                    d = json.load(f)
                dic = d["calibration"]
                shared_dict["calib_x0"], shared_dict["calib_x1"], shared_dict["calib_y0"], shared_dict["calib_y1"] = dic["x0"], dic["x1"], dic["y0"], dic["y1"]
                shared_dict["calib_pass"] = True

        elif 'Output' in id:
            now = datetime.datetime.now()
            iFile = now.strftime('%Y%m%d_%H%M%S')
            file = filedialog.asksaveasfilename(filetypes = fTyp, initialdir = iDir, initialfile = iFile)
            if not file == "":
                d = {"calibration": {"x0": shared_dict["calib_x0"], "x1": shared_dict["calib_x1"], "y0": shared_dict["calib_y0"], "y1": shared_dict["calib_y1"]}}
                with open(file + ".json", 'w') as f:
                    json.dump(d, f)
        root.destroy()

    @eel.expose
    def RecordFunctions(id):
        if id == 'Start':
            for cam in camname:
                if record[cam]['mode'] == 0:
                    q_log.put('Video capture start')
                    data_cam[cam]['fps'] = node_cam[cam]['fps_now']
                    #data_cam['cam2']['fps'] = node_cam['cam2']['fps_now']
                    record[cam]['timer_s'] = time.perf_counter()
                    record[cam]['mode'] = 1

        if id == 'End':
            for cam in camname:
                if record[cam]['mode'] == 1:
                    record[cam]['mode'] = 2
                    record[cam]['timer_e'] = time.perf_counter()

                    q_log.put('Video capture end')

                    theory_frame = (record[cam]['timer_e']-record[cam]['timer_s']) * data_cam[cam]['fps']

                    #cp = 'cam1'
                    if record[cam]['framenum'] - 2 < theory_frame and theory_frame < record[cam]['framenum'] + 2:
                        q_log.put('Cam1 ok. Frame: %d, Time: %.2f' % (record[cam]['framenum'], record[cam]['timer_e']-record[cam]['timer_s']))
                        record[cam]['accuracy'] = 1
                    else:
                        if theory_frame - record[cam]['framenum'] < 0:
                            q_log.put('Cam1 error. Frame: %d, Time: %.2f, Overframe: %d' % (record[cam]['framenum'], record[cam]['timer_e']-record[cam]['timer_s'], int(record[cam]['framenum'] - theory_frame)))

                        if theory_frame - record[cam]['framenum'] >0:
                            q_log.put('Cam1 error. Frame: %d, Time: %.2f, Lackframe: %d' % (record[cam]['framenum'], record[cam]['timer_e']-record[cam]['timer_s'], int(theory_frame - record[cam]['framenum'])))

                        record[cam]['accuracy'] = 2

                    record[cam]['mode'] = 3

        if id == 'Set':
            if record['cam1']['mode'] == 0 and record['cam2']['mode'] == 0 and n_cam == 2:
                node_cam['cam2']['fps_now'] = node_cam['cam1']['fps_now']

                GUINodeChange('Side', 'fps', node_cam['cam2']['fps_now'], ['now'], 'textbox')
                GUINodeChange('Side', 'fps', node_cam['cam2']['fps_now'], ['now'], 'trackbar')

        if id == 'Cancel':
            for cam in camname:
                record[cam]['saveselect'] = 2

        if id == 'Capture':
            for cam in camname:
                if record[cam]['capture'] == 0:
                    record[cam]['capture'] = 1

        if 'Gray' in id:
            if 'Bottom' in id:
                data_cam['cam1']['color'] = False
            elif 'Side' in id:
                data_cam['cam2']['color'] = False

        elif 'Color' in id:
            if 'Bottom' in id:
                data_cam['cam1']['color'] = True
            elif 'Side' in id:
                data_cam['cam2']['color'] = True

    @eel.expose
    def CameraNodeChange(id, val):
        idpass = ''
        cp = ''
        if 'Bottom' in id:
            idpass = 'Bottom'
            cp = 'cam1'
        elif 'Side' in id:
            idpass = 'Side'
            cp = 'cam2'

        if 'trackbar' in id:
            val = val/100
        elif 'textbox' in id:
            val = val

        if 'Exposure' in id:
            if val > node_cam[cp]['exptime_max'] or val < node_cam[cp]['exptime_min']:
                val = node_cam[cp]['exptime_now']
                GUINodeChange(idpass, 'exp', val, ['now'], 'textbox')
                GUINodeChange(idpass, 'exp', val, ['now'], 'trackbar')
                return
            else:
                node_cam[cp]['exptime_now'] = val

            if 'trackbar' in id:
                GUINodeChange(idpass, 'exp', val, ['now'], 'textbox')

            if 'textbox' in id:
                GUINodeChange(idpass, 'exp', val, ['now'], 'trackbar')

        if 'Gain' in id:
            if val > node_cam[cp]['gain_max'] or val < node_cam[cp]['gain_min']:
                val = node_cam[cp]['gain_now']
                GUINodeChange(idpass, 'gain', val, ['now'], 'textbox')
                GUINodeChange(idpass, 'gain', val, ['now'], 'trackbar')
                return
            else:
                node_cam[cp]['gain_now'] = val

            if 'trackbar' in id:
                GUINodeChange(idpass, 'gain', val, ['now'], 'textbox')

            if 'textbox' in id:
                GUINodeChange(idpass, 'gain', val, ['now'], 'trackbar')

        if 'Framerate' in id:
            if val > node_cam[cp]['fps_max'] or val < node_cam[cp]['fps_min']:
                val = node_cam[cp]['fps_now']
                GUINodeChange(idpass, 'fps', val, ['now'], 'textbox')
                GUINodeChange(idpass, 'fps', val, ['now'], 'trackbar')
                return
            else:
                node_cam[cp]['fps_now'] = val

            node_cam[cp]['exptime_max'] = (0.99 * (10 ** 6)) / val
            GUINodeChange(idpass, 'exp', node_cam[cp]['exptime_max'], ['max'], 'trackbar')
            if node_cam[cp]['exptime_now'] > node_cam[cp]['exptime_max']:
                GUINodeChange(idpass, 'exp', node_cam[cp]['exptime_now'], ['now'], 'textbox')

            if 'trackbar' in id:
                GUINodeChange(idpass, 'fps', val, ['now'], 'textbox')

            if 'textbox' in id:
                GUINodeChange(idpass, 'fps', val, ['now'], 'trackbar')

    @eel.expose
    def js2py(val, variable):
        try:
            if val.isdecimal():
                val = float(val)
            elif 'True' in val:
                val = True
            elif 'False' in val:
                val = False
        except:
            pass
        shared_dict[variable] = val
        #print(type(val), val, variable)

    #"""

    def GUIinit():
        catearr = ['textbox', 'trackbar',]
        cnt = n_cam + 1
        if n_cam == 0:
            cnt = 2
        for i in range(1, cnt):
            for key, val in node_cam['cam' + str(i)].items():
                for c in catearr:
                    if i == 1:
                        cp = 'Bottom'
                    elif i == 2:
                        cp = 'Side'
                    category = c
                    
                    arr = ['max', 'min', 'now']
                    for state in arr:
                        if state in key:
                            GUINodeChange(cp, key, val, state, category)


    #"""
    def GUINodeChange(cp, key, val, state, category):
        id = ''
        if 'exp' in key:
            id = cp + 'Exposure'
        if 'gain' in key:
            id = cp + 'Gain'
        if 'fps' in key:
            id = cp + 'Framerate'

        if not ('now' in state and category == 'textbox'):
            val = 100 * val
        eel.GUINodeChange(id, val, state, category)


    #"""

    while node_cam['cam1']['exptime_now'] <= 0.0 and node_cam['cam1']['fps_now'] <= 0.0 and flag.value:
        continue

    eel.init('script')
    eel.start("html/index.html", size=(600, 700), position=(960, 0), close_callback=onCloseWindow, block=False, port = 8002)

    GUIinit()
    GUIinit()
    
    #py2js
    while True:
        run = False
        
        if flag == False:
            break
        
        if shared_dict['calib_pass']:
            arr = ["x0", "x1", "y0", "y1"]
            for val in arr:
                eel.jsChangeValue("calib_" + val, int(shared_dict["calib_" + val]))
            shared_dict['calib_pass'] = False

        if not q_log.empty():
            string = q_log.get()
            eel.PrintLog(string)
            run = True

        for cam in camname:
            if record[cam]['mode'] == 1:
                eel.jsChangeText('FrameCount', record['cam1']['framenum'])
                run = True

        if not q_py2js.empty():
            run = True
            py2js_dict = q_py2js.get()
        
            if py2js_dict['Function'] == "Create":

                if py2js_dict['repeat'] == 1:
                    eel.CreateObj(py2js_dict['parentid'], py2js_dict['id'], py2js_dict['tagName'], py2js_dict['val'])
                else:
                    for i in range(py2js_dict['repeat']):
                        val = py2js_dict['val'][i]

                        if type(val) == np.int32:
                            val = int(val)
                        eel.CreateObj(py2js_dict['parentid'], str(py2js_dict['id'][i]), py2js_dict['tagName'][i], val)

                eel.BR(py2js_dict['parentid'])

            elif py2js_dict['Function'] == "Delete":
                if py2js_dict['repeat'] == 1:
                    eel.DeleteObj(py2js_dict['id'])
                else:
                    for i in range(py2js_dict['repeat']):
                        eel.DeleteObj(py2js_dict['id'][i])

            elif py2js_dict['Function'] == "Hide":
                if py2js_dict['repeat'] == 1:
                    eel.HideObj(py2js_dict['id'])

            elif py2js_dict['Function'] == "Show":
                if py2js_dict['repeat'] == 1:
                    eel.ShowObj(py2js_dict['id'])

        if run == True:
            eel.sleep(0.001)
        else:
            eel.sleep(0.3)

