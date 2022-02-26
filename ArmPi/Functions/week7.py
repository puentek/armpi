#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import numpy as np
import time
import math 
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
range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),}

class Perception():
    def __init__(self):
        self.cam = Camera.Camera()
        self.cam.camera_open()
        
    def __del__(self):
        self.cam.camera_close()

    def setTargetColor(target_color):
        global __target_color
        #print("COLOR", target_color)
        __target_color = ('red',)
        __target_color = target_color
        return (True, ())
    
    def getAreaMaxContour(self, mask, contours):
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
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

    def getColorContour(self,fig_img ,target_colors ):
        area_max = 0
        color_detect = None
        largest_contour = None
        for i in color_range: 
                if i in target_colors:
                    color_mask = cv2.inRange(
                        fig_img, color_range[color_detect][0], color_range[color_detect][1]
                    )
                    contour, area = self.getAreaMaxContour(color_mask)
                    if contour is not None and area > area_max:
                        largest_contour = contour
                        detected_color = i
                        area_max = area

        return largest_contour, detected_color, area_max
        
  

    def calc_center (self, contour, img_size= (640, 480)):
        
        #unreachable = False
        
        roi = getROI(box)
        img_x, img_y = calc_center(rect, roi, img_size, square_length) 
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))
        world_x, world_y = convertCoordinate(img_x, img_y, img_size) 
        return (world_x, world_y), box

    def detect(self, img, target_colors=("red",)):
        fig_img =  cv2.cv2Color(img, cv2.COLOR_BGR2LAB)
        contour, color, area = self.getColorContour(fig_img, target_colors)

        if contour is None:
            return None, 0, None, None
        else:
            center, box = self.calc_center(contour)
            return center, area, color, box

    def draw_detect(self,img,center, color, box):
        img = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        if box is not None:
            cv2.drawContours(img, [box], -1, range_rgb[color], 2)
            cv2.putText(
                img,
                f"({center[0]}, {center[1]})",
                (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                range_rgb[color],
                1,
            )
        return img

    def dist(self, j1, j2, j_dist):
        j11, j12 = j1 # distance between 
        j21, j22 = j2
        j_dist = math.sqrt((j21-j11)**2 * (j22-j12)**2)
        return j_dist
    
    def try_detect(
        self,
        min_time=1.5,
        max_distance=0.3,
        min_area=2500,
        timeout=10,
        show=False,
        size=(640, 480),
    ):

        color_init = None
        centers = []
        time_init = time.time()
        detect_init = None 

        while time.time - time_init <= timeout:
            img = self.cam.frame 
            if img is None:
                logging.debug(f"you may continue")
            img = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
            img = cv2.GaussianBlur(img, (11, 11), 11)
            center, area, color, box = self.detect(img)

            if show:
                frame = self.draw_detection(img, center, color, box)
                cv2.imshow("frame", frame) 
                logging.debug(f"frame is being shown")
                
            if center is None or area < min_area:
                logging.debug(f"you may continue")

            
            if len(centers) == 0:
                distance = 0
                logging.debug(f"distance is zero ")
            else:
                distance = self.dist(center, centers[-1])
                logging.debug(f"distance between centers- else cond", distance)

            # Reset 
            if distance > max_distance or color != color_init:
                centers = []
                color_init = None
                detect_init = None
                logging.debug(f"you may continue")

            # make changes to the centers 
            if detect_init is None:
                detect_init = time.time()
                color_init = color
                logging.debug(f"appenfing in process", centers)
            centers.append(center)

            # averages
            if time.time() - detect_init > min_time:
                centers = np.array(centers)
                x, y = np.mean(centers, axis=0)
                logging.debug(f"coordinates and colors detect",(x,y))
                return (x, y), color


        raise TimeoutError



if __name__ == "__main__":
    detector = Perception()
    
    try:
        while True:
            try:
                (x, y), color = detector.try_detect()
                logging.debug(f"This was a sucess !! color: {color} at {x},{y} ")
            except TimeoutError:
                logging.debug(f"There has been no detection :( ")
    except KeyboardInterrupt:
        logging.debug(f"This is the end")

    
    cv2.destroyAllWindows()