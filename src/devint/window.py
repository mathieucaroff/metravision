import cv2
import numpy as np

import util
from util import Namespace

import devint.multiView
import devint.progressBar


class MvWindow:
    def __init__(self, logger, windowConfig, videoName, backgroundMode, playbackStatus, jumpToFrameFunction):
        self.logger = logger
        windowName = windowConfig.name
        if backgroundMode:
            windowName = "Bg" + windowName
        self.windowName = windowName
        cv2.namedWindow(windowName)
        self.windowConfig = windowConfig
        self.windowShape = windowShape = [windowConfig.size.height, windowConfig.size.width]
        self.videoName = videoName
        self.backgroundMode = backgroundMode
        self.redCrossEnabled = windowConfig.redCrossEnabled
        if backgroundMode:
            self.backgroundModeTextFrame = np.full(shape = [50, 400], fill_value = [255], dtype=np.uint8)
            cv2.putText(
                img = self.backgroundModeTextFrame, text = "[background mode]", org = (12, 30),
                fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1,
                color = [0], thickness = 2
            )

        mouseCallbackList = []
        def mouseCallbackDispatcher(event, x, y, flags, param):
            for fun in mouseCallbackList:
                fun(event, x, y, flags, param)

        cv2.setMouseCallback(windowName, mouseCallbackDispatcher)

        height = self.windowConfig.progressBar.height
        displayShape = (windowShape[0] - height, windowShape[1])
        self.updateSubWindows = devint.multiView.setupVideoSelectionHook(
            self.windowConfig.multiView,
            mouseCallbackList,
            displayShape,
            playbackStatus,
            self.windowClosed
        )
        devint.progressBar.setupClickHook(mouseCallbackList, windowShape, 30, jumpToFrameFunction)

    def windowClosed(self, windowName):
        """Checking for a property of the window to tell whether it is (still) open."""
        v = {"visible": cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE), "windowName": windowName}
        v["different"] = v["visible"] != 1.0
        if v["different"]:
            self.logger.info(f"Window {windowName} closed")
        return v["different"]


    def update(self, imageSet, advancementPercentage):
        # Display the resulting frame
        shape = (*self.windowShape, 3)
        output = np.zeros(shape = shape, dtype = np.uint8)
        barHeight = self.windowConfig.progressBar.height

        devint.multiView.renderNimages(
            videoName = self.videoName, 
            imageSet = imageSet,
            output = output[:-barHeight]
        )
        devint.progressBar.drawBar(self.windowConfig.progressBar, buffer = output, advancementPercentage = advancementPercentage)
        if self.backgroundMode:
            cv2.imshow(self.windowName, self.backgroundModeTextFrame)
        else:
            cv2.imshow(self.windowName, output)

        self.updateSubWindows(imageSet = imageSet)


    def waitkey(self, controlledTime, playbackStatus):
        key = 0xFF & cv2.waitKey(max(0, int(1000 * controlledTime)) + 1)
        spacebar = 0x20
        if key == spacebar:
            playbackStatus.play = not playbackStatus.play
        if key == ord('q'):
            playbackStatus.quitting = True
        if key == ord('s'):
            playbackStatus.endReached = True
        if key == ord('f'):
            playbackStatus.refreshNeeded = True
        if key == ord('d'):
            raise util.DeveloperInterruption
        if self.redCrossEnabled:
            if self.windowClosed(self.windowName):
                playbackStatus.quitting = True
