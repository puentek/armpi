#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
import logging
logging.basicConfig(level=logging.DEBUG)

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()
# comment

class Perception(object):
    def __init__(range_rgb, __target_color):
        range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),}
        
        __target_color = ('red',)
        return __target_color
        

    def setTargetColor(target_color):
        global __target_color
        #print("COLOR", target_color)
        __target_color = target_color
        return (True, ())
    
    def getAreaMaxContour(contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  #
            contour_area_temp = math.fabs(cv2.contourArea(c))  # calculation of outline area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # max area profile is valid only if the area is greater than 300 to filter interference
                    area_max_contour = c

        return area_max_contour, contour_area_max


    #initial position 
    def initMove():
        servo1 = 500
        Board.setBusServoPulse(1, servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
    
    def setBuzzer(timer):
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)
    
    def set_rgb(color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def reset():
        global count
        global track
        global _stop
        global get_roi
        global first_move
        global center_list
        global __isRunning
        global detect_color
        global action_finish
        global start_pick_up
        global __target_color
        global start_count_t1
        
        count = 0
        _stop = False
        track = False
        get_roi = False
        center_list = []
        first_move = True
        __target_color = ()
        detect_color = 'None'
        action_finish = True
        start_pick_up = False
        start_count_t1 = True

