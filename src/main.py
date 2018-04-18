import numpy as np
# import matplotlib.pyplot as plt
import cv2
import time
import random

import collections

from util import Namespace, printMV, printMVerr
import ihm.window as window
from ihm.progressBar import setupClickHook
from ihm.multiView import setupVideoSelectionHook

import parseConfig

import sys
print(sys.version)


glob = Namespace()

def jumpTo(cap, fraction):
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frameIndex = int(fraction * frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)

def main():
    with open("metravision.config.yml") as configFile:
        config = parseConfig.MvConfig.fromConfigFile(configFile)

    videoPath = random.choice(config.video.files)
    try:
        open(videoPath).close()
    except FileNotFoundError:
        printMVerr(f"The specified video {videoPath} coudln't be open. (Missing file?)")
        raise

    cap = cv2.VideoCapture(videoPath)

    def jumpToFrameFunction(advancementPercentage):
        jumpTo(cap, advancementPercentage)

    height = 800
    width = 960
    windowName = "Metravision"
    cv2.namedWindow(windowName)
    setupClickHook(windowName, (height, width), 30, jumpToFrameFunction)

    updateWindows = setupVideoSelectionHook(windowName)

    lecture(cap, updateWindows)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def lecture(cap, updateWindows):
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    timePerFrame = 1 / fps

    jumpTo(cap, random.random() * 3 / 4)

    last_fgMask = np.zeros((height, width), dtype = np.uint8) # Temporary value

    bgSub = cv2.createBackgroundSubtractorMOG2()

    referenceTime = time.clock()
    for loopIndex in range(1_000_000_000):
        im = collections.OrderedDict()
        #! viewSet = im

        # Capture frame-by-frame
        ok, im["frame"] = cap.read()

        if not ok:
            return "break", None

        analyse(bgSub, im, last_fgMask)

        # End of image operations
        last_fgMask = im["fgMask"]

        # Display the resulting frame
        advancementPercentage = cap.get(cv2.CAP_PROP_POS_FRAMES) / frameCount
        window.window(im, advancementPercentage, updateWindows)

        controlledTime = (referenceTime + timePerFrame * loopIndex) - time.clock()
        continuing = window.waitkey(controlledTime)
        last_fgMask = im["fgMask"]

        if continuing == "break":
            break


def analyse(bgSub, im, last_fgMask):
    im["fgMask"] = bgSub.apply(image = im["frame"]) # , learningRate = 0.5)

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

def easyKernel(size, sizeX = None):
    """Generate an OpenCV kernel objet of given size.
    Note: I haven't checked the sizeX parameter"""
    sizeY = size
    if sizeX is None:
        sizeX = size
    return cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (sizeY, sizeX) )


if __name__ == "__main__":
    main()
