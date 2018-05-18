import collections

import random
import time

import cv2

# import matplotlib.pyplot as plt

from util import printMV
import util

import analyse

class PlaybackStatus:
    __slots__ = ["play", "quitting", "refreshNeeded", "debugNeeded"]
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
    frameIndex = property()

    def getData(self):
        data = [(0.6, "Moto"), (4.5, "Automobile")]
        # self.analyseTool.data
        return data

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
        """Plays the video, frame by frame, or wait for the video to be unpaused, until quitting."""
        self.timeController.init()
        while not self.playbackStatus.quitting:
            if self.playbackStatus.play or self.playbackStatus.refreshNeeded:
                self.playbackStatus.refreshNeeded = False
                controlledTime = self.timeController.getControlledTime()
                mvWindow.waitkey(controlledTime, self.playbackStatus, self.redCrossEnabled)

                imageSet = collections.OrderedDict()

                self.playbackStatus.quitting, imageSet["frame"] = self.getFrame()
                if self.playbackStatus.quitting:
                    break

                assert imageSet["frame"] is not None

                self.analyseTool.run(imageSet, self.frameIndex)

                advancementPercentage = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.frameCount
                mvWindow.update(imageSet, advancementPercentage)

                controlledTime = self.timeController.getControlledTime()
                mvWindow.waitkey(controlledTime, self.playbackStatus, self.redCrossEnabled)
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

    @frameIndex.getter
    def frameIndex(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)
    
    @frameIndex.setter
    def frameIndex(self, index):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    
    def reachedEnd(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_COUNT) - self.frameIndex <= 1

    def getFrame(self):
        quitting = False
        notOkCount = 0
        ok = False
        while not ok:
            ok, frame = self.cap.read()
            if not ok:
                if self.reachedEnd():
                    quitting = True
                    break
                notOkCount += 1
                if notOkCount >= 3:
                    printMV("Not ok >= 3 -- quitting.")
                    quitting = True
                    break
            else:
                notOkCount = 0
        return quitting, frame
