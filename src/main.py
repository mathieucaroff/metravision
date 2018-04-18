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
print(sys.version)


glob = Namespace()

def jumpTo(cap, fraction):
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frameIndex = int(fraction * frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)

def main():
    with open("metravision.config.yml") as configFile:
        config = parseConfig.MvConfig.fromConfigFile(configFile)

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

    updateWindows = window.setup(
        windowName = "Metravision",
        windowShape = windowShape,
        jumpToFrameFunction = jumpToFrameFunction)

    lecture(cap, updateWindows, windowShape)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def lecture(cap, updateWindows, windowShape):
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    timePerFrame = 1 / fps

    jumpTo(cap, random.random() * 3 / 4)

    last_fgMask = np.zeros((height, width), dtype = np.uint8) # Temporary value

    # Background subtractor initialisation
    bgSub, blobDetector = analyse.setupAnalyseTools()

    referenceTime = time.clock()
    for loopIndex in range(1_000_000_000):
        im = collections.OrderedDict()
        #! viewSet = im

        # Capture frame-by-frame
        ok, im["frame"] = cap.read()

        analyse.analyse(bgSub, blobDetector, im, last_fgMask)

        # End of image operations
        last_fgMask = im["fgMask"]

        # Display the resulting frame
        advancementPercentage = cap.get(cv2.CAP_PROP_POS_FRAMES) / frameCount
        window.window(im, advancementPercentage, updateWindows, windowShape)

        controlledTime = (referenceTime + timePerFrame * loopIndex) - time.clock()
        continuing = window.waitkey(controlledTime)
        last_fgMask = im["fgMask"]

        if continuing == "break" or not ok:
            break


if __name__ == "__main__":
    main()
