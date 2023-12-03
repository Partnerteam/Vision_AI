import os
import time
import datetime
import cv2
import threading
import sms
import Jetson.GPIO as GPIO
from ultralytics import YOLO
from pathlib import Path


model = YOLO("blender.pt")
now = datetime.datetime.now()
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
hour = now.strftime("%H_%M")
os.makedirs('../blackbox/%s/%s/%s' % (year, month, day), exist_ok=True)
b_path = '../blackbox/%s/%s/%s/%s' % (year, month, day, hour)
save_path = str(Path(b_path).with_suffix('.avi'))
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter(save_path, fourcc, 25.0, (640, 480))
cap = cv2.VideoCapture(0)
motor_flag = False


def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def warn_alam():
    sms.send_sms(1042914448)
    print('119 신고')

    for x in range(5):
        os.system('mpg123 warn.mp3')
        time.sleep(2)


def motor_work():
    print('모터작동')
   
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(21, GPIO.OUT)                 # 모터
    GPIO.setup(23, GPIO.OUT) 
    
    GPIO.output(21, GPIO.LOW)
    GPIO.output(23, GPIO.HIGH)
    print('모터를 켭니다.')

    time.sleep(30)


def emergency_situation():
    print('비상상황')

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)                 # 비상 경광등
    GPIO.output(21, GPIO.HIGH)
    GPIO.output(23, GPIO.LOW)

    time.sleep(30)


def machine_start():
    global motor_flag
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(19, GPIO.OUT)
        GPIO.output(19, GPIO.LOW)   
        auth_cnt = 0
        cnt = 0
        while True:
            if cnt % 300000 == 0:
                ret, frame = cap.read()
                if ret == False:
                    break
                kneader = model.predict(source=frame, conf=0.88, show=True, save=True)
                if not kneader[0].boxes:
                    if not motor_flag:
                        auth_cnt = 0
                        threading.Thread(target=motor_work).start()
                        motor_flag = True
                for r in kneader:
                    for c in r.boxes.cls:
                        if model.names[int(c)] == 'normal' or model.names[int(c)] == 'long_spatula':
                            if not motor_flag:
                                auth_cnt = 0
                                threading.Thread(target=motor_work).start()
                                motor_flag = True
                        elif model.names[int(c)] == 'arms' or model.names[int(c)] == 'etc':
                            auth_cnt += 1
                            if auth_cnt > 1:
                                threading.Thread(target=emergency_situation).start()
                                threading.Thread(target=warn_alam()).start()
                                motor_flag = False
                out.write(frame)
            cnt += 1
    except:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
        if get_dir_size('../blackbox') > 4000000000:
            for x in range(1, 12):
                tmp = str(int(month) - x)
                del_month = tmp.zfill(2)
                os.system('rm -rf ../blackbox/{0}/{1}'.format(year, del_month))


if __name__ == "__main__":
    machine_start()




