import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
import random

from util import Namespace
from ihm.multiView import viewDimensionsFromN, renderNimages
from ihm.progressBar import drawBar

import preTraitement

def main():
    videoPath = "C:\\pi\\Sequences6min\\DerniereSequences.avi"
    videoPath = "C:\\pi\\SequencesCourtes\\embouteillage-21s.mp4"
    videoPath = "C:\\pi\\SequencesCourtes\\bouchon-40s.mp4"

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
        action, fgMask = loop(frameIdx, timePerFrame, startTime, height, width, cap, bgSub, fgMask)
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
        gx, gy = x, y

cv2.namedWindow('View')
cv2.setMouseCallback("View", evListener)

# Create a black image, a window and bind the function to window

def loop(frameIdx, timePerFrame, startTime, height, width, cap, bgSub, last_fgMask):
    # Capture frame-by-frame
    ok, frame = cap.read()

    if not ok:
        return "break", None

    fgMask = bgSub.apply(image = frame) # , learningRate = 0.5)
    # glob.fgMask = fgMask

    if last_fgMask is None:
        last_fgMask = fgMask

    # Two-frame and
    bitwise_fgMask_and = cv2.bitwise_and(fgMask, last_fgMask)

    # erodeAndDilate
    mask = bitwise_fgMask_and

    erodeA = 2
    dilateA = 30
    erodeB = 35
    dilateB = 30 # erodeA + erodeB - dilateA

    mask = cv2.erode(mask, easyKernel(erodeA))
    erodeMaskA = mask

    mask = cv2.dilate(mask, easyKernel(dilateA))
    dilateMaskA = mask
    
    mask = cv2.erode(mask, easyKernel(erodeB))
    erodeMaskB = mask

    mask = cv2.dilate(mask, easyKernel(dilateB))
    dilateMaskB = mask

    # edMask = mask

    bitwise_fgMask_dilateB_and = cv2.bitwise_and(mask, fgMask)

    # End of image operations
    last_fgMask = fgMask

    # Display the resulting frame
    height = 960
    width = 960
    shape = (height, width, 3)
    output = np.zeros(shape = shape, dtype = np.uint8)
    imageList = [frame, fgMask, bitwise_fgMask_and, erodeMaskA, dilateMaskB, bitwise_fgMask_dilateB_and]
    renderNimages(imageList, output = output)
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
    return "continue", fgMask

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
