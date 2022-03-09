#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

# 夹持器夹取时闭合的角度
servo1 = 500

def initMove():
    Board.setBusServoPulse(1, servo1 - 50, 500)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

__isRunning = False
def reset():
    initMove()

def init():
    global __isRunning
    reset()
    __isRunning = True
    print("Calibration Init")

def start():
    global __isRunning
    __isRunning = True
    print("Calibration Start")

def stop():
    global __isRunning
    __isRunning = False
    print("Calibration Stop")

def exit():
    global __isRunning
    __isRunning = False
    print("Calibration Exit")

def run(img):
    global __isRunning
    
    if not __isRunning:
        return img
    
    img_h, img_w = img.shape[:2]
    cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 255), 2)
    cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 255), 2)
    return img

if __name__ == '__main__':
    init()
    start()
    my_camera = Camera.Camera()
    my_camera.camera_open()
    kernel = np.ones((5, 5), np.uint8)
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = run(frame)           
            # converting the image to HSV format
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # defining the lower and upper values of HSV,
            # this will detect yellow colour
            Lower_hsv = np.array([60, 40, 40])
            Upper_hsv = np.array([150, 255, 255])
            
            # creating the mask by eroding,morphing,
            # dilating process
            Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
            # gray = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
            # (thresh, blackAndWhiteImage) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            Mask = cv2.bitwise_not(Mask)
            Mask = cv2.erode(Mask, kernel, iterations=1) 
            Mask = cv2.dilate(Mask, kernel, iterations=1)   
            cv2.imshow('Frame', Mask)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
