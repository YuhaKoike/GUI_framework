import time
import numpy as np
from multiprocessing import Process, Manager, Value, Queue

import script.py.init as init
#process
import script.py.gui as gui
import script.py.savevideo as savevideo
import script.py.getframe as getframe
import script.py.display as display


def MultiProcessManeger():
    dict_arr = init.HTMLinit()

    # set cam number
    dict_cam = init.count_cam()
    if dict_cam['num'] == -1:
        return

    #shared value
    flag = Value('i', True)

    #queue
    q_py2js = Queue()

    q_byte_image1 = Queue()
    q_rec_image1 = Queue()
    q_cap_image1 = Queue()

    q_byte_image2 = Queue()
    q_rec_image2 = Queue()
    q_cap_image2 = Queue()

    q_log = Queue()

    #dict share memory
    manager = Manager()

    info_cam = manager.dict(dict_cam)

    data_cam1_dict = {'fps': 0, 'width': 0, 'height': 0, 'rotate': 0, 'color': False}
    data_cam2_dict = {'fps': 0, 'width': 0, 'height': 0, 'rotate': 0, 'color': False}
    data_cam1 = manager.dict(data_cam1_dict)
    data_cam2 = manager.dict(data_cam2_dict)
    data_cam_dict = {'cam1': data_cam1, 'cam2': data_cam2,}
    
    node_cam1_dict = {'exptime_now':0, 'exptime_max':0, 'exptime_min':0, 'gain_now':0, 'gain_max':0, 'gain_min':0, 'fps_now': 0, 'fps_max':0, 'fps_min':0}
    node_cam2_dict = {'exptime_now':0, 'exptime_max':0, 'exptime_min':0, 'gain_now':0, 'gain_max':0, 'gain_min':0, 'fps_now': 0, 'fps_max':0, 'fps_min':0}
    node_cam1 = manager.dict(node_cam1_dict)
    node_cam2 = manager.dict(node_cam2_dict)
    node_dict = {'cam1': node_cam1, 'cam2': node_cam2}

    record_dict_cam1 = {'mode':0, 'saveselect':0, 'framenum': 0, 'accuracy': 0, 'capture':0, 'timer_s': 0.0, 'timer_e': 0.0, 'folder': 'C:/', 'filename': ''}
    record_dict_cam2 = {'mode':0, 'saveselect':0, 'framenum': 0, 'accuracy': 0, 'capture':0, 'timer_s': 0.0, 'timer_e': 0.0, 'folder': 'C:/', 'filename': ''}
    dict_cam1 = manager.dict(record_dict_cam1)
    dict_cam2 = manager.dict(record_dict_cam2)
    record_dict = {'cam1': dict_cam1, 'cam2': dict_cam2}
    
    shared_dict = manager.dict(dict_arr)
    data_cam = manager.dict(data_cam_dict)
    node_cam = manager.dict(node_dict)
    record = manager.dict(record_dict)

    #append process
    n_cam = info_cam['num']
    CamAcquation = []
    if n_cam == 0:
        CamAcquation.append(Process(target=getframe.cam1, args=(flag, "cam1", info_cam["cam1"], q_byte_image1, q_rec_image1, q_cap_image1, data_cam["cam1"], node_cam["cam1"], record["cam1"])))
    elif n_cam == 1:
        CamAcquation.append(Process(target=getframe.cam1, args=(flag,"cam1", info_cam["cam1"], q_byte_image1, q_rec_image1, q_cap_image1, data_cam["cam1"], node_cam["cam1"], record["cam1"])))
    elif n_cam == 2:
        CamAcquation.append(Process(target=getframe.cam1, args=(flag, "cam1", info_cam["cam1"], q_byte_image1, q_rec_image1, q_cap_image1, data_cam["cam1"], node_cam["cam1"], record["cam1"])))
        CamAcquation.append(Process(target=getframe.cam1, args=(flag, "cam2", info_cam["cam2"], q_byte_image2, q_rec_image2, q_cap_image2, data_cam["cam2"], node_cam["cam2"], record["cam2"])))
    else:
        flag.value = False
    HtmlGui = Process(target=gui.GuiMenu, args=(flag, q_log, shared_dict, node_cam, data_cam, n_cam, record, q_py2js))
    Record = Process(target=savevideo.RecordMovie, args=(flag, q_log, info_cam, q_rec_image1, q_rec_image2, q_cap_image1, q_cap_image2, data_cam, node_cam, record))
    Display = Process(target=display.Display, args=(flag, shared_dict, q_py2js, n_cam, q_byte_image1, q_byte_image2, data_cam, node_cam))

    #start process
    for i,p in enumerate(CamAcquation):
        if i != 0:
            #複数クラスが同時にカメラにアクセスするとエラーになるっぽい
            time.sleep(4)
        p.start()
    HtmlGui.start()
    Record.start()
    Display.start()
    
    while True:
        #terminate()するなら各プロセスにflag送らなくてよくね？→いずれかのプロセスが終了されたことを知りたい
        time.sleep(2)
        if flag.value == False:
            for p in CamAcquation:
                p.terminate()
            Display.terminate()
            HtmlGui.terminate()
            Record.terminate()
            break