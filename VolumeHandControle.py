import cv2
import numpy as np
import time
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 800, 600 

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
vol = 0
volBar = 200
volPer = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volume.GetVolumeRange()
volume.SetMasterVolumeLevel(-20.0, None)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw= False)
    
    RED = (0, 0, 255)
    ORANGE = (0, 174, 255)
    GREEN = (0, 255, 0)

    if len(lmList) > 0:
        lm4 = lmList[4]
        lm8 = lmList[8]
        
        xlm4, ylm4 = lm4[1], lm4[2]
        xlm8, ylm8 = lm8[1], lm8[2]
        xLine, yLine = (xlm4+xlm8) // 2, (ylm4+ylm8) // 2

        lineLength = math.hypot(xlm8-xlm4, ylm8-ylm4)
        minLineLength = 10        # 10
        maxLineLength = 180       # 180
        
        
        if lineLength > 155: 
            color = RED
        if 165 > lineLength > 100: 
            color = ORANGE
        if lineLength < 100: 
            color = GREEN
            
        cv2.circle(img, (xlm8, ylm8), 10, color, cv2.FILLED)
        cv2.line(img, (xlm4, ylm4), (xlm8, ylm8), color, 4)
        
        # Draw a circle on thumb finger (4) index finger (8) and at the middle of the line 
        cv2.circle(img, (xlm4, ylm4), 8, color, cv2.FILLED)
        cv2.circle(img, (xlm8, ylm8), 8, color, cv2.FILLED)
        cv2.circle(img, (xLine, yLine), 6, color, cv2.FILLED)
        
        # Manage Volume
        volRange= volume.GetVolumeRange()
        minVol = volRange[0]
        maxVol = volRange[1]
        vol = np.interp(lineLength, [minLineLength, maxLineLength], [minVol, maxVol])
        volBar = np.interp(lineLength, [minLineLength, maxLineLength], [200, 90])
        volPer= np.interp(lineLength, [minLineLength, maxLineLength], [0, 100])
        # print(lineLength, vol)
        volume.SetMasterVolumeLevel(vol, None)
        
        # Draw volume pourcentage 
        cv2.rectangle(img, (10, 90), (30, 200), color, 3)
        cv2.rectangle(img, (15, int(volBar)), (30, 200), color, -1)
        cv2.putText(img, f"{int(volPer)}%", (30, 220), cv2.FONT_HERSHEY_PLAIN, 1.5, color, 3)
        
        
        

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"FPS:{int(fps)}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1.5, ORANGE, 3)
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)