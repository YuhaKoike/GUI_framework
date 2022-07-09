import cv2
import datetime
import time
import os
import re
import shutil


def delete_image(img_record):
    for i in range(img_record.qsize()):
        img_record.get()
        print('\r' + 'Delete frame %d...' % i, end='') 

def cap(img, cap_name, cam):
    cap_img = img.get()
    cap_img = cv2.cvtColor(cap_img, cv2.COLOR_BAYER_BG2BGR)
    if cam['color'] == False:
        if len(cap_img.shape[:]) != 2:
            if cap_img.shape[2] == 3:
                cap_img = cv2.cvtColor(cap_img, cv2.COLOR_BGR2GRAY)

    cv2.imwrite(cap_name, cap_img)

def duplicate_rename(file_path):
    if os.path.exists(file_path):
        name, ext = os.path.splitext(file_path)
        i = 1
        while True:
            # 数値を3桁などにしたい場合は({:0=3})とする
            new_name = "{} ({}){}".format(name, i, ext)
            if not os.path.exists(new_name):
                return new_name
            i += 1
    else:
        return file_path

#real time save
def RecordMovie(flag, q_log, info_cam, q_rec_image1, q_rec_image2, q_cap_image1, q_cap_image2, data_cam, node_cam, record):
    rec_image = {'cam1': q_rec_image1, 'cam2':q_rec_image2}
    cap_image = {'cam1': q_cap_image1, 'cam2': q_cap_image2}

    rec_init = {'cam1': False, 'cam2': False}
    capture = {'cam1': None, 'cam2': None}
    
    cnt = info_cam['num'] + 1
    if info_cam['num'] == 0:
        cnt = 2

    while flag.value:
        run = False
        for i in range(1, cnt):
            cp = 'cam' + str(i)
            if not rec_image[cp].empty():
                run = True
                byte_image = rec_image[cp].get()
                bgr_image = cv2.cvtColor(byte_image, cv2.COLOR_BAYER_BG2BGR)
                if not data_cam[cp]['color']:
                    if len(bgr_image.shape[:]) != 2:
                        if bgr_image.shape[2] == 3:
                            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

                if rec_init[cp] == False:
                    videoname = record[cp]['folder'] + record[cp]['filename'] + '_{}.avi'.format(cp)
                    videoname = duplicate_rename(videoname)

                    q_log.put('Saving Video ...')

                    fourcc = 0
                    framerate = data_cam[cp]['fps']
                    size = (int(data_cam[cp]['width']), int(data_cam[cp]['height']))
                    capture[cp] = cv2.VideoWriter(videoname, fourcc, framerate, size, data_cam[cp]['color'])

                    rec_init[cp] = True

                if 'bgr_image' in locals():
                    capture[cp].write(bgr_image)
                    del bgr_image

            if record[cp]['mode'] == 3 and rec_image[cp].empty() == True:
                run = True
                capture[cp].release()

                for i, key in enumerate(record[cp].items()):
                    if i < 5 and i != 2:
                        record[cp][key[0]] = 0
                    elif i == 2:
                        record[cp][key[0]] = 0

                q_log.put(cp + ' saved video')
                rec_init[cp] = False

            if record[cp]['saveselect'] == 2:
                run = True
                if rec_image[cp].empty() == False:
                    delete_image(rec_image[cp])

                for i, key in enumerate(record[cp].items()):
                    if i < 5 and i != 2:
                        record[cp][key[0]] = 0
                    elif i == 2:
                        record[cp][key[0]] = 0

                record[cp]['filename'] = ''
                rec_init[cp] = False
                q_log.put('Do not save video')

            if record[cp]['capture'] == 2:
                run = True
                if cap_image[cp].empty() == False:
                    capname = record[cp]['folder'] + record[cp]['filename'] + '_{}.bmp'.format(cp)
                    capname = duplicate_rename(capname)

                    cap(cap_image[cp], capname, data_cam[cp])

                    q_log.put(cp + ' chapture image')

                    record[cp]['capture'] = 0
                    record[cp]['filename'] = ''

        if run == False:
            time.sleep(1)