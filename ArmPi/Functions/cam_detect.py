from pickle import FALSE, TRUE
import cv2
import sys
sys.path.append('/home/pi/ArmPi/')
import Calibrating 
import Camera
import time
import logging



def no_motion(my_camera):
    threshold = 20
    while threshold == 20:
        frame_1 = 
        frame_2 = 
        frame_i = fps = 16
        for i in range(0, frame_i*5):
            frame_new = ()
            frame_final = frame_new-frame_i
        v = sum(abs(frame_final))
        if v < threshold:
            status = TRUE
            logging.debug("current status: ", status)
            
        else: 
            status = FALSE
            logging.debug("current status: ", status)

    return status

if __name__ == '__main__':
    init()
    start()
    my_camera = Camera.Camera()
    my_camera.camera_open()
    while True:
        img = my_camera.frame
        #hand will begin to move
        if img is not None:
        # if false hand will not move
            key = cv2.waitKey(1)
            if key == 27:
                break
    
    my_camera.camera_close()
    cv2.destroyAllWindows()
