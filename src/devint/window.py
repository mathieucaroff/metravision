import cv2
import numpy as np

import util
from util import Namespace
from util import printMV

import  devint.multiView
import devint.progressBar


def windowClosed(windowName):
    """Checking for a property of the window to tell whether it is (still) open."""
    v = {"visible": cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE), "windowName": windowName}
    v["different"] = v["visible"] != 1.0
    if v["different"]:
        printMV(f"Window {windowName} closed")
    return v["different"]


class MvWindow:
    def __init__(self, windowName, windowShape, videoName, playbackStatus, jumpToFrameFunction):
        cv2.namedWindow(windowName)
        self.windowName = windowName
        self.windowShape = windowShape
        self.videoName = videoName

        mouseCallbackList = []
        def mouseCallbackDispatcher(event, x, y, flags, param):
            for fun in mouseCallbackList:
                fun(event, x, y, flags, param)

        cv2.setMouseCallback(windowName, mouseCallbackDispatcher)


        bp = Namespace()
        bp.bgCol = [255, 255, 255]
        bp.fgCol = [255, 191, 127]
        bp.shape = (30, windowShape[1])
        self.barProperties = bp


        displayShape = (windowShape[0] - bp.shape[0], windowShape[1])
        self.updateSubWindows = devint.multiView.setupVideoSelectionHook(mouseCallbackList, displayShape, playbackStatus, windowClosed)
        devint.progressBar.setupClickHook(mouseCallbackList, windowShape, 30, jumpToFrameFunction)


    def update(self, imageSet, advancementPercentage):
        # Display the resulting frame
        shape = (*self.windowShape, 3)
        output = np.zeros(shape = shape, dtype = np.uint8)
        barHeight = self.barProperties.shape[0]

        devint.multiView.renderNimages(self.videoName, imageSet, output = output[:-barHeight])
        devint.progressBar.drawBar(self.barProperties, buffer = output, advancementPercentage = advancementPercentage)
        cv2.imshow("Metravision", output)

        self.updateSubWindows(imageSet = imageSet)


    def waitkey(self, controlledTime, playbackStatus, redCrossEnabled):
        key = 0xFF & cv2.waitKey(max(0, int(1000 * controlledTime)) + 1)
        spacebar = 0x20
        if key == spacebar:
            playbackStatus.play = not playbackStatus.play
        if key == ord('q'):
            playbackStatus.quitting = True
        if key == ord('f'):
            playbackStatus.refreshNeeded = True
        if key == ord('d'):
            raise util.DeveloperInterruption
        if redCrossEnabled:
            if windowClosed(self.windowName):
                playbackStatus.quitting = True
