import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
import random

import collections

from util import Namespace
from ihm.multiView import viewDimensionsFromN, renderNimages
from ihm.progressBar import drawBar

import parseConfig

def main():
    with open("metravision.config.yml") as configFile:
        config = parseConfig.MvConfig.fromConfigFile(configFile)
    
    videoPath = random.choice(config.video.files)
    cv2.namedWindow('View')
    cv2.setMouseCallback("View", evListener)

    cap = cv2.VideoCapture(videoPath)

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)

    jumpTo(cap, random.random() / 2)

    timePerFrame = 1 / fps

    fgMask = np.zeros((height, width), dtype = np.uint8) # Temporary value

    bgSub = cv2.createBackgroundSubtractorMOG2()

    startTime = time.clock()
    for frameIdx in range(1_000_000_000):
        action, fgMask = loopActions(frameIdx, timePerFrame, startTime, height, width, cap, bgSub, fgMask)
        if action == "break":
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

windowNameSet = set()
glob = Namespace()

glob.x = -1
glob.y = -1

def wImshow(winName, content):
    windowNameSet.add(winName)
    if (glob.x, glob.y) != (-1, -1):
        cv2.circle(content, (glob.x, glob.y), 100, (255, 0, 0), -1)
        glob.x, glob.y = -1, -1        
    cv2.imshow(winName, content)


def evListener(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(x, y)
        glob.x = x
        glob.y = y

# Create a black image, a window and bind the function to window

def loopActions(frameIdx, timePerFrame, startTime, height, width, cap, bgSub, last_fgMask):
    im = collections.OrderedDict()
    #! viewSet = im

    # Capture frame-by-frame
    ok, im["frame"] = cap.read()

    if not ok:
        return "break", None

    im["fgMask"] = bgSub.apply(image = im["frame"]) # , learningRate = 0.5)
    # glob.fgMask = fgMask

    if last_fgMask is None:
        last_fgMask = im["fgMask"]

    # Two-frame and
    im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], last_fgMask)

    # erodeAndDilate
    mask = im["bitwise_fgMask_and"]

    erodeA = 2
    dilateA = 30
    erodeB = 35
    dilateB = 30 # erodeA + erodeB - dilateA

    mask = cv2.erode(mask, easyKernel(erodeA))
    im["erodeMaskA"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateA))
    im["dilateMaskA"] = mask
    
    mask = cv2.erode(mask, easyKernel(erodeB))
    im["erodeMaskB"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateB))
    im["dilateMaskB"] = mask

    # edMask = mask

    im["bitwise_fgMask_dilateB_and"] = cv2.bitwise_and(mask, im["fgMask"])

    # End of image operations
    last_fgMask = im["fgMask"]

    # Display the resulting frame
    height = 960
    width = 960
    shape = (height, width, 3)
    output = np.zeros(shape = shape, dtype = np.uint8)
    #! viewSet = im
    renderNimages(im.values(), output = output)
    barProperties = Namespace()
    barProperties.bgCol = [255, 255, 255]
    barProperties.fgCol = [255, 191, 127]
    barProperties.height = 30
    drawBar(barProperties, buffer = output, advancementPercentage = frameIdx / 1000)
    wImshow("View", output)

    controlledTime = (startTime + timePerFrame * frameIdx) - time.clock()
    if cv2.waitKey(max(0, int(1000 * controlledTime)) + 1) & 0xFF == ord('q'):
        return "break", None
    if any(map(windowClosed, windowNameSet)):
        return "break", None
    return "continue", im["fgMask"]

def windowClosed(windowName):
    """Checking for a property of the window to tell whether it is (still) open."""
    return cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) != 1

def easyKernel(size, sizeX = None):
    """Generate an OpenCV kernel objet of given size.
    Note: I haven't checked the sizeX parameter"""
    sizeY = size
    if sizeX is None:
        sizeX = size
    return cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (sizeY, sizeX) )

def jumpTo(cap, fraction):
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frameIndex = int(fraction * frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)

if __name__ == "__main__":
    main()
