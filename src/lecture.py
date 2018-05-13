import collections

import random
import time

import cv2

# import matplotlib.pyplot as plt

from util import printMV
import util

import analyse

class PlaybackStatus:
    __slots__ = ["play", "quitting", "refreshNeeded"]
    def __init__(self, play = True, quitting = False, refreshNeeded = False):
        self.play = play
        self.quitting = quitting
        self.refreshNeeded = refreshNeeded


class TimeController:
    """
    To ensure a regular time flow in the application.
    """
    def __init__(self, timePerFrame):
        self.timePerFrame = timePerFrame
        self.init()
    
    def init(self):
        self.referenceTime = time.clock()
        self.timeIndex = 0

    def getControlledTime(self):
        self.timeIndex += 1
        controlledTime = (self.referenceTime + self.timePerFrame * self.timeIndex) - time.clock()
        if controlledTime < -0.5:
            # Reset the time reference -- the program is too late, catching up will have perceptible effect on the playback.
            self.init()
        if controlledTime <= 0:
            controlledTime = 0
        return controlledTime


class Lecteur:
    __slots__ = "redCrossEnabled analyseTool playbackStatus timeController cap frameCount height width fps timePerFrame vidDimension".split()

    def __init__(self, cap, redCrossEnabled, debug):
        self.initVideoInfo(cap)
        self.redCrossEnabled = redCrossEnabled

        # Background subtractor initialisation
        self.analyseTool = analyse.AnalyseTool(vidDimension = self.vidDimension, debug = debug)

        self.playbackStatus = PlaybackStatus(play = True)
        self.timeController = TimeController(self.timePerFrame)

        self.jumpTo(random.random() * 3 / 4)


    @util.logged
    def run(self, mvWindow):
        self.timeController.init()
        while not self.playbackStatus.quitting:
            if self.playbackStatus.play or self.playbackStatus.refreshNeeded:
                self.playbackStatus.refreshNeeded = False
                controlledTime = self.timeController.getControlledTime()
                mvWindow.waitkey(controlledTime, self.playbackStatus, self.redCrossEnabled)

                imageSet = collections.OrderedDict()

                # Capture frame-by-frame
                ok = False
                notOkCount = 0
                while not ok:
                    ok, imageSet["frame"] = self.cap.read()
                    if not ok:
                        notOkCount += 1
                        if self.cap.isOpened():
                            printMV(f"Not ok! cap.isOpened() ::: {util.typeVal(self.cap.isOpened())}")
                        if notOkCount >= 3:
                            printMV("Not ok >= 3 -- break")
                            raise RuntimeError
                    else:
                        notOkCount = 0

                assert ok
                assert imageSet["frame"] is not None

                self.analyseTool.run(imageSet)

                advancementPercentage = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.frameCount
                mvWindow.update(imageSet, advancementPercentage)
            else:
                duration = 0.05
                mvWindow.waitkey(duration, self.playbackStatus, self.redCrossEnabled)


    def initVideoInfo(self, cap):
        self.cap = cap
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.timePerFrame = 1 / self.fps
        self.vidDimension = (self.height, self.width)


    def jumpTo(self, fraction):
        frameCount = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frameIndex = int(fraction * frameCount)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
        self.playbackStatus.refreshNeeded = True
