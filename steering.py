from imutils.video import VideoStream
import numpy as np

import cv2
import imutils
import time

from directKey import  W, A, S, D
from directKey import PressKey, ReleaseKey 

greenLower = np.array([36, 25, 25])
greenUpper = np.array([70, 255,255])

video = VideoStream(src=0).start()
 
time.sleep(2.0)
initial = True
flag = False
current_key_pressed = set()
circle_radius = 30
windowSize = 80
windowSize2 = 100

lr_counter = 0

while True:
    keyPressed = False
    keyPressed_lr = False
    
    frame = video.read()
    
    frame = cv2.flip(frame,1);

    frame = imutils.resize(frame, width=600)
    frame = imutils.resize(frame, height=300)

    height = frame.shape[0]
    width = frame.shape[1]
    
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    up_mask = mask[0:height//2,0:width,]
    down_mask = mask[height//2:height,width//4:3*width//4,]

    cnts_up = cv2.findContours(up_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_up = imutils.grab_contours(cnts_up)
    center_up = None

    cnts_down = cv2.findContours(down_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_down = imutils.grab_contours(cnts_down)
    center_down = None
 
    if len(cnts_up) > 0:

        c = max(cnts_up, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center_up = (int(M["m10"] / (M["m00"]+0.000001)), int(M["m01"] / (M["m00"]+0.000001)))
    
        if radius > circle_radius:
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center_up, 5, (0, 0, 255), -1)

            if center_up[0] < (width//2 - windowSize//2):
                PressKey(A)
                current_key_pressed.add(A)
                keyPressed = True
                keyPressed_lr = True
            elif center_up[0] > (width//2 + windowSize//2):
                PressKey(D)
                current_key_pressed.add(D)
                keyPressed = True
                keyPressed_lr = True
    
    if len(cnts_down) > 0:
        c2 = max(cnts_down, key=cv2.contourArea)
        ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
        M2 = cv2.moments(c2)
        center_down = (int(M2["m10"] / (M2["m00"]+0.000001)), int(M2["m01"] / (M2["m00"]+0.000001)))
        center_down = (center_down[0]+width//4,center_down[1]+height//2)
    
        if radius2 > circle_radius:
            cv2.circle(frame, (int(x2)+width//4, int(y2)+height//2), int(radius2),
                (0, 255, 255), 2)
            cv2.circle(frame, center_down, 5, (0, 0, 255), -1)
            
            if (height//2) < center_down[1] < ((3*height)//4) and (width//4) < center_down[0] < ((3*width)//4):
                PressKey(W)
                keyPressed = True
                current_key_pressed.add(W)
            elif center_down[1] > ((3*height)//4 + 20) and (width//4) < center_down[0] < ((3*width)//4):
                PressKey(S)
                keyPressed = True
                current_key_pressed.add(S)
            

    frame_copy = frame.copy()
    
    frame_copy = cv2.rectangle(frame_copy,(0,0),(width//2- windowSize//2,height//2 ),(255,255,255),1)
    cv2.putText(frame_copy,'LEFT',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255))

    frame_copy = cv2.rectangle(frame_copy,(width//2 + windowSize//2,0),(width-2,height//2 ),(255,255,255),1)
    cv2.putText(frame_copy,'RIGHT',(438,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255))

    frame_copy = cv2.rectangle(frame_copy,(width//4,(height//2)+5),(3*width//4,3*height//4),(255,255,255),1)
    cv2.putText(frame_copy,'UP',(width//4,(height//2)+33),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255))

    frame_copy = cv2.rectangle(frame_copy,(width//4,((3*height)//4)+5),(3*width//4,height),(255,255,255),1)
    cv2.putText(frame_copy,'DOWN',((3*width//4)-100,(height//2)+108),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255))

    cv2.imshow("Frame", frame_copy)

    if not keyPressed and len(current_key_pressed) != 0:
        for key in current_key_pressed:
            ReleaseKey(key)
        current_key_pressed = set()

    if not keyPressed_lr and ((A in current_key_pressed) or (D in current_key_pressed)):
        if A in current_key_pressed:
            ReleaseKey(A)
            current_key_pressed.remove(A)
        elif D in current_key_pressed:
            ReleaseKey(D)
            current_key_pressed.remove(D)

    key = cv2.waitKey(1) & 0xFF
 
    if key == ord("q"):
        break
 

video.stop()
cv2.destroyAllWindows()