import numpy as np
# import matplotlib.pyplot as plt
import cv2
import time
import random

import collections

from util import Namespace, printMV, printMVerr
import ihm.window as window
from ihm.progressBar import setupClickHook

import parseConfig

import sys
print(sys.version)


glob = Namespace()


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
    setupClickHook("Metravision", (height, width), 30, jumpToFrameFunction)

    lecture(cap)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def lecture(cap):
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    timePerFrame = 1 / fps

    jumpTo(cap, random.random() * 3 / 4)

    last_fgMask = np.zeros((height, width), dtype = np.uint8) # Temporary value

    # Background subtractor initialisation
    bgSub = cv2.createBackgroundSubtractorMOG2()

    # blobDetector initialisation
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 1_000
    params.maxArea = 50_000
    params.minDistBetweenBlobs = 1
    blobDetector = cv2.SimpleBlobDetector_create(params)

    referenceTime = time.clock()
    for loopIndex in range(1_000_000_000):
        im = collections.OrderedDict()
        #! viewSet = im

        # Capture frame-by-frame
        ok, im["frame"] = cap.read()

        analyse(bgSub, blobDetector, im, last_fgMask)

        # End of image operations
        last_fgMask = im["fgMask"]

        # Display the resulting frame
        advancementPercentage = cap.get(cv2.CAP_PROP_POS_FRAMES) / frameCount
        window.window(im, advancementPercentage)

        controlledTime = (referenceTime + timePerFrame * loopIndex) - time.clock()
        continuing = window.waitkey(controlledTime)
        last_fgMask = im["fgMask"]

        if continuing == "break":
            break


def analyse(bgSub, blobDetector, im, last_fgMask):
    im["fgMask"] = bgSub.apply(image = im["frame"]) # , learningRate = 0.5)

    # Two-frame and
    im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], last_fgMask)

    # erodeAndDilate
    mask = im["bitwise_fgMask_and"]

    erodeA = 4
    dilateA = 20
    erodeB = 26
    dilateB = 15 # previously erodeA + erodeB - dilateA
    dilateC = 4

    mask = cv2.erode(mask, easyKernel(erodeA))
    im["erodeMaskA"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateA))
    im["dilateMaskA"] = mask

    mask = cv2.erode(mask, easyKernel(erodeB))
    im["erodeMaskB"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateB))
    im["dilateMaskB"] = mask

    # edMask = mask

    mask = cv2.bitwise_and(mask, im["fgMask"])
    im["bitwise_fgMask_dilateB_and"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateC))
    im["dilateC"] = mask

    # Contour
    red = (0, 0, 255)
    """ 
    img, contourPointList, hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    im["dilateMaskA"] = cv2.cvtColor(im["dilateMaskA"], cv2.COLOR_GRAY2BGR)

    allContours = -1
    cv2.drawContours(
        image = im["dilateMaskA"],
        contours = contourPointList,
        contourIdx = allContours,
        color = red
    ) """

    # Blob Detector
    imageNameList = list(im.keys()) # Buffered
    for imageName in imageNameList:
        if not "dilate" in imageName:
            continue
        blobKeypoints = blobDetector.detect(255 - im[imageName])
        im[f"blob_{imageName}"] = cv2.drawKeypoints(
            image = im[imageName],
            keypoints = blobKeypoints,
            outImage = np.array([]),
            color = red,
            flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )

    # cv2.cvtColor(im["dilateMaskB"], cv2.COLOR_GRAY2BGR)

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
