import collections

import random
import time

import cv2
import numpy as np
# import matplotlib.pyplot as plt

from util import printMV

import analyse

def lecture(cap, mvWindow, redCrossEnabled, glob):
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    timePerFrame = 1 / fps

    jumpTo(cap, random.random() * 3 / 4)

    last_fgMask = np.zeros((height, width), dtype = np.uint8) # Temporary value
    oneBeforeLast_fgMask = last_fgMask

    # Background subtractor initialisation
    analyseTool = analyse.AnalyseTool()
    trackerList = []

    referenceTime = time.clock()
    timeIndex = 0
    while True:
        im = collections.OrderedDict()
        #! viewSet = im

        # Capture frame-by-frame
        ok = False
        notOkCount = 0
        while not ok:
            ok, im["frame"] = cap.read()
            if not ok:
                notOkCount += 1
                printMV(f"Not ok! isOpened():{cap.isOpened()}")
                if notOkCount >= 3:
                    printMV("Not ok >= 3 -- break")
                    break
            else:
                notOkCount = 0

        # trackerList = analyseTool.run(trackerList, im, last_fgMask, oneBeforeLast_fgMask, glob)

        # End of image operations
        # oneBeforeLast_fgMask = last_fgMask
        # last_fgMask = im["fgMask"]

        # Display the resulting frame
        advancementPercentage = cap.get(cv2.CAP_PROP_POS_FRAMES) / frameCount
        mvWindow.update(im, advancementPercentage)

        timeIndex += 1
        controlledTime = (referenceTime + timePerFrame * timeIndex) - time.clock()
        print(controlledTime)
        if controlledTime < -0.5:
            # Reset the time reference -- the program is too late, catching up will have effect on the playback.
            referenceTime = time.clock()
            timeIndex = 0
        continuing = mvWindow.waitkey(controlledTime, redCrossEnabled)
        # last_fgMask = im["fgMask"]

        if continuing == "break":
            break


def jumpTo(cap, fraction):
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frameIndex = int(fraction * frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)