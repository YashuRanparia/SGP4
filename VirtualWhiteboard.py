import math
import os
import time

import cv2
import numpy as np

import HandTrackingModule as htm

###
brushThickness = 15
eraserThickness = 50
###
folderPath = "header"
myList = os.listdir(folderPath)
# print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)
print(len(overlayList))

header = overlayList[0]
drawColor = (0, 0, 255)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

fps = cap.get(cv2.CAP_PROP_FPS)

# imgCanvas.fill(255)
while True:
    start = time.time()
    # import image
    success, img = cap.read()
    img = cv2.flip(img, 1)
    # find hand landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList)
        # tip of index and middle fingers
        x0, y0 = lmList[4][1:]
        x3, y3 = lmList[8][1:]
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        #center point of the tip
        x = (x0+x3)//2
        y = (y0+y3)//2

        #Calculate the distance of the thumb tip and index tip
        dis = math.sqrt(((x3-x0) ** 2) + ((y3-y0) ** 2))

        # check when fingers up
        fingers = detector.fingersUp()
        # selection mode - two fingers up
        # condition = fingers[1] and fingers[2]
        condition = False
        condition2 = fingers[0] and fingers[1] and (dis < 200)

        if condition:
            xp, yp = 0, 0
            print("Selection time")
            # waiting for the click
            if y1 < 115:
                if 250 < x1 < 400:
                    header = overlayList[0]
                    drawColor = (0, 0, 255)
                elif 470 < x1 < 640:
                    header = overlayList[1]
                    drawColor = (255, 0, 0)
                elif 690 < x1 < 845:
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                elif 880 < x1 < 1050:
                    header = overlayList[3]
                    drawColor = (0, 0, 0)
                elif 1080 < x1 < 1280:
                    imgCanvas.fill(0)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # draw mode - index finger up
        if condition2:
            cv2.circle(img, (x, y), 15, drawColor, cv2.FILLED)
            print("Drawing time")
            if xp == 0 and yp == 0:
                xp, yp = x, y

            # cv2.line(img, (xp,xp), (x1,y1), drawColor, brushThickness)
            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x, y), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x, y), drawColor, eraserThickness)

            else:
                cv2.line(img, (xp, yp), (x, y), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x, y), drawColor, brushThickness)
            xp, yp = x, y

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)


    img[0:100, 0:1280] = header  # setting in our header image
    # img = cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)
    cv2.imshow("Image", img)
    end = time.time()
    processing_time = end - start
    delay = int((1000 / fps) - processing_time)

    if cv2.waitKey(delay) & 0xFF == ord('q'): # wait for the delay or until the user presses q
        break
    # cv2.imshow("Canvas", imgCanvas)
    # cv2.waitKey(0)


# import pyautogui
# pyautogui.moveTo(200, 300, duration=2)
