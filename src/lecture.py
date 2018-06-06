import collections

import time

import cv2

# import matplotlib.pyplot as plt

import util

import analyse.processing as processing

class PlaybackStatus:
    __slots__ = "play endReached quitting refreshNeeded".split()
    def __init__(self, play = True, endReached = False, quitting = False, refreshNeeded = False):
        self.play = play
        self.endReached = endReached
        self.quitting = quitting
        self.refreshNeeded = refreshNeeded


class TimeController:
    """
    Ensures a regular time flow in the application. Prevents the time to flow faster than the recorded video time.
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
    __slots__ = "cap frameCount height width fps timePerFrame vidDimension".split()
    __slots__ += "redCrossEnabled jumpEventSubscriber".split()
    __slots__ += "logger processingTool playbackStatus timeController".split()
    frameIndex = property()

    def getData(self):
        # data = [(0.6, "Moto"), (4.5, "Automobile")]
        data = self.processingTool.getData()
        return data

    def __init__(self, logger, cap, redCrossEnabled, playbackStatus):
        self.initVideoInfo(cap)
        self.logger = logger

        self.redCrossEnabled = redCrossEnabled
        self.jumpEventSubscriber = []

        # Background subtractor initialisation
        self.processingTool = processing.ProcessingTool(self.logger, vidDimension = self.vidDimension, timePerFrame = self.timePerFrame, jumpEventSubscriber = self.jumpEventSubscriber)

        self.playbackStatus = playbackStatus
        self.timeController = TimeController(self.timePerFrame)

    def run(self, mvWindow):
        """Plays the video, frame by frame, or wait for the video to be unpaused, until end of video or quitting."""
        self.timeController.init()
        while not (self.playbackStatus.endReached or self.playbackStatus.quitting):
            if self.playbackStatus.play or self.playbackStatus.refreshNeeded:
                self.playbackStatus.refreshNeeded = False
                controlledTime = self.timeController.getControlledTime()
                util.timed(mvWindow.waitkey)(controlledTime, self.playbackStatus, self.redCrossEnabled)

                imageSet = collections.OrderedDict()

                self.playbackStatus.endReached, frame = self.getFrame()
                if self.playbackStatus.endReached:
                    break
                
                imageSet["frame"] = frame
                imageSet["video"] = frame[:]

                self.processingTool.run(imageSet, self.frameIndex)

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

        for f in self.jumpEventSubscriber:
            f(cap = self.cap, playbackStatus = self.playbackStatus, frameIndex = frameIndex)

    @frameIndex.getter
    def frameIndex(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)
    
    @frameIndex.setter
    def frameIndex(self, index):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    
    def reachedEnd(self):
        return self.frameIndex >= self.cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1

    def getFrame(self):
        endReached = False
        notOkCount = 0
        ok = False
        while not ok:
            ok, frame = self.cap.read()
            if not ok:
                if self.reachedEnd():
                    endReached = True
                    break
                notOkCount += 1
                if notOkCount >= 3:
                    self.logger.debug("Not ok >= 3 -- endReached.")
                    endReached = True
                    break
            else:
                notOkCount = 0
        assert frame is not None or endReached
        return endReached, frame
