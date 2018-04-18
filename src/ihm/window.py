import cv2
import numpy as np

from util import Namespace

import ihm.progressBar
import ihm.multiView


def setup(windowName, windowShape, jumpToFrameFunction):
    cv2.namedWindow(windowName)

    mouseCallbackList = []
    def mouseCallbackDispatcher(event, x, y, flags, param):
        for fun in mouseCallbackList:
            fun(event, x, y, flags, param)
    
    cv2.setMouseCallback(windowName, mouseCallbackDispatcher)

    updateWindows = ihm.multiView.setupVideoSelectionHook(mouseCallbackList)
    ihm.progressBar.setupClickHook(mouseCallbackList, windowShape, 30, jumpToFrameFunction)
    
    return updateWindows


def window(imageSet, advancementPercentage, updateWindows, windowShape):
    # Display the resulting frame
    shape = (*windowShape, 3)
    output = np.zeros(shape = shape, dtype = np.uint8)
    barProperties = Namespace()
    barProperties.bgCol = [255, 255, 255]
    barProperties.fgCol = [255, 191, 127]
    barHeight = 30
    barProperties.shape = (barHeight, shape[1])

    ihm.multiView.renderNimages(imageSet, output = output[:-barHeight])
    ihm.progressBar.drawBar(barProperties, buffer = output, advancementPercentage = advancementPercentage)
    cv2.imshow("Metravision", output)

    updateWindows(imageSet = imageSet, windowShape = windowShape)


def waitkey(controlledTime):
    continuing = "continue"
    if cv2.waitKey(max(0, int(1000 * controlledTime)) + 1) & 0xFF == ord('q'):
        continuing = "break"
    if False and windowClosed("Metravision"):
        print("Window closed")
        continuing = "break"
    return continuing


def windowClosed(windowName):
    """Checking for a property of the window to tell whether it is (still) open."""
    return cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) != 1
