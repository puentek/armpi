from pickle import FALSE, TRUE
import cv2
import sys
sys.path.append('/home/pi/ArmPi/')
import Calibrating 
import Camera
import time
import logging

logging.basicConfig(level=logging.DEBUG)

def run(img):
    global __isRunning
    
    if not __isRunning:
        return img
    
    img_h, img_w = img.shape[:2]
    cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 255), 2)
    cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 255), 2)
    return img

def get_mask(frame):
    kernel = np.ones((5, 5), np.uint8)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
    # defining the lower and upper values of HSV,
    # this will detect blue colour
    Lower_hsv = np.array([60, 40, 40])
    Upper_hsv = np.array([125, 255, 255])
    
    # creating the mask by eroding,morphing,
    # dilating process
    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    # gray = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
    # (thresh, blackAndWhiteImage) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # Mask = cv2.bitwise_not(Mask)
    Mask = cv2.erode(Mask, kernel, iterations=1) 
    Mask = cv2.dilate(Mask, kernel, iterations=4)
    return Mask
    
def no_motion(my_camera):
    threshold = 20
    # while threshold == 20:
    img = my_camera.frame
    status = False
    print("img: ", img)
    if img is not None:
        f = img.copy()
        frame_i = get_mask(f) 
        fps = 16
        for i in range(0, fps*5):
            img = my_camera.frame
            if img is not None:
                f = img.copy()
                frame_new = get_mask(f)
                frame_final = frame_new-frame_i
                v = np.sum(np.abs(frame_final))
                logging.debug(f"value: {v}")

                if v < threshold:
                    status = True
                    logging.debug("current status: ", status)
                    
                else: 
                    status = False
                    logging.debug("current status: ", status)
                cv2.imshow('Frame', frame_new)            
                key = cv2.waitKey(1)
                if key == 27:
                    break
    return status

if __name__ == '__main__':
    # init()
    # start()
    my_camera = Camera.Camera()
    my_camera.camera_open()
    i = 0
    while i < 10:
        status = no_motion(my_camera)
        img = my_camera.frame
        i = i + 1
        #hand will begin to move
    my_camera.camera_close()
    cv2.destroyAllWindows()