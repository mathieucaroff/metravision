import numpy as np
# import matplotlib.pyplot as plt
import cv2
import time
import random

import collections

from util import Namespace, printMV, printMVerr
import ihm.window as window

import parseConfig

import analyse

import sys
printMV(sys.version)

sys.path[:0] = ["src", "."]

glob = Namespace()

def jumpTo(cap, fraction):
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frameIndex = int(fraction * frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)

def main():
    with open("metravision.config.yml") as configFile:
        config = parseConfig.MvConfig.fromConfigFile(configFile)

    windowName = config.raw.windowName
    windowHeight = config.raw["window"]["height"]
    windowWidth = config.raw["window"]["width"]
    windowShape = (windowHeight, windowWidth)

    videoPath = random.choice(config.video.files)
    try:
        open(videoPath).close()
    except FileNotFoundError:
        printMVerr(f"The specified video {videoPath} coudln't be open. (Missing file?)")
        raise

    cap = cv2.VideoCapture(videoPath)

    def jumpToFrameFunction(advancementPercentage):
        jumpTo(cap, advancementPercentage)

    updateWindows, barProperties = window.setup(
        windowName = windowName,
        windowShape = windowShape,
        jumpToFrameFunction = jumpToFrameFunction)

    lecture(cap, windowName, updateWindows, windowShape, barProperties, config.raw.redCrossEnabled)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def lecture(cap, windowName, updateWindows, windowShape, barProperties, redCrossEnabled):
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    timePerFrame = 1 / fps

    jumpTo(cap, random.random() * 3 / 4)

    last_fgMask = np.zeros((height, width), dtype = np.uint8) # Temporary value
    oneBeforeLast_fgMask = last_fgMask

    # Background subtractor initialisation
    bgSub, blobDetector, mvTrackerCreator = analyse.setupAnalyseTools()
    trackerList = []

    referenceTime = time.clock()
    for loopIndex in range(1_000_000_000):
        im = collections.OrderedDict()
        #! viewSet = im

        # Capture frame-by-frame
        ok = False
        notOkCount = 0
        while not ok:
            ok, im["frame"] = cap.read()
            if not ok:
                notOkCount += 1
                printMV("Not ok!")
                if notOkCount >= 3:
                    printMV("Not ok >= 3 -- break")
                    break
            else:
                notOkCount = 0

        trackerList = analyse.analyse(bgSub, blobDetector, mvTrackerCreator, trackerList, im, last_fgMask, oneBeforeLast_fgMask, glob)

        # End of image operations
        oneBeforeLast_fgMask = last_fgMask
        last_fgMask = im["fgMask"]

        # Display the resulting frame
        advancementPercentage = cap.get(cv2.CAP_PROP_POS_FRAMES) / frameCount
        window.window(im, advancementPercentage, updateWindows, windowShape, barProperties)

        controlledTime = (referenceTime + timePerFrame * loopIndex) - time.clock()
        continuing = window.waitkey(windowName, controlledTime, redCrossEnabled)
        last_fgMask = im["fgMask"]

        if continuing == "break":
            break


if __name__ == "__main__":
    main()
