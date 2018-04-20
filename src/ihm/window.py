import cv2
import numpy as np

from util import Namespace
from util import printMV

import ihm.progressBar
import ihm.multiView


def setup(windowName, windowShape, jumpToFrameFunction):
    cv2.namedWindow(windowName)

    mouseCallbackList = []
    def mouseCallbackDispatcher(event, x, y, flags, param):
        for fun in mouseCallbackList:
            fun(event, x, y, flags, param)
    
    cv2.setMouseCallback(windowName, mouseCallbackDispatcher)

    updateWindows = ihm.multiView.setupVideoSelectionHook(mouseCallbackList, windowShape)
    ihm.progressBar.setupClickHook(mouseCallbackList, windowShape, 30, jumpToFrameFunction)
    
    barProperties = Namespace()
    barProperties.bgCol = [255, 255, 255]
    barProperties.fgCol = [255, 191, 127]
    barProperties.shape = (30, windowShape[1])

    return updateWindows, barProperties


def window(imageSet, advancementPercentage, updateWindows, windowShape, barProperties):
    # Display the resulting frame
    shape = (*windowShape, 3)
    output = np.zeros(shape = shape, dtype = np.uint8)
    barHeight = barProperties.shape[0]

    ihm.multiView.renderNimages(imageSet, output = output[:-barHeight])
    ihm.progressBar.drawBar(barProperties, buffer = output, advancementPercentage = advancementPercentage)
    cv2.imshow("Metravision", output)

    updateWindows(imageSet = imageSet)


def waitkey(windowName, controlledTime, redCrossEnabled):
    continuing = "continue"
    if cv2.waitKey(max(0, int(1000 * controlledTime)) + 1) & 0xFF == ord('q'):
        continuing = "break"
    if redCrossEnabled:
        if windowClosed(windowName):
            printMV("Window closed")
            continuing = "break"
    return continuing


def windowClosed(windowName):
    """Checking for a property of the window to tell whether it is (still) open."""
    v = {"visible": cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE)}
    v["different"] = v["visible"] != 1.0
    return v["different"]
