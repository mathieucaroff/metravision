import cv2
import numpy as np

from util import Namespace
from util import printMV

import ihm.progressBar
import ihm.multiView


class MvWindow:
    def __init__(self, windowName, windowShape, jumpToFrameFunction):
        cv2.namedWindow(windowName)
        self.windowName = windowName
        self.windowShape = windowShape

        mouseCallbackList = []
        def mouseCallbackDispatcher(event, x, y, flags, param):
            for fun in mouseCallbackList:
                fun(event, x, y, flags, param)
        
        cv2.setMouseCallback(windowName, mouseCallbackDispatcher)

        self.updateSubWindows = ihm.multiView.setupVideoSelectionHook(mouseCallbackList, windowShape)
        ihm.progressBar.setupClickHook(mouseCallbackList, windowShape, 30, jumpToFrameFunction)
        
        bp = Namespace()
        bp.bgCol = [255, 255, 255]
        bp.fgCol = [255, 191, 127]
        bp.shape = (30, windowShape[1])
        self.barProperties = bp


    def update(self, imageSet, advancementPercentage):
        # Display the resulting frame
        shape = (*self.windowShape, 3)
        output = np.zeros(shape = shape, dtype = np.uint8)
        barHeight = self.barProperties.shape[0]

        ihm.multiView.renderNimages(imageSet, output = output[:-barHeight])
        ihm.progressBar.drawBar(self.barProperties, buffer = output, advancementPercentage = advancementPercentage)
        cv2.imshow("Metravision", output)

        self.updateSubWindows(imageSet = imageSet)


    def waitkey(self, controlledTime, redCrossEnabled):
        continuing = "continue"
        if cv2.waitKey(max(0, int(1000 * controlledTime)) + 1) & 0xFF == ord('q'):
            continuing = "break"
        if redCrossEnabled:
            if self.windowClosed():
                printMV("Window closed")
                continuing = "break"
        return continuing

    def windowClosed(self):
        """Checking for a property of the window to tell whether it is (still) open."""
        v = {"visible": cv2.getWindowProperty(self.windowName, cv2.WND_PROP_VISIBLE)}
        v["different"] = v["visible"] != 1.0
        return v["different"]
