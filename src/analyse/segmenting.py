from enum import Enum

import util
from util import printMV

class AnalyseData:
    def __init__(self, timePerFrame, jumpEventSubscriber, segmenter):
        """
        Beware, the analyse data / segmenter thing is a real mess.
        Ideally, you should remove the "AnalyseData" class, and only use RealSegmenter.

        Sorry to my future self too, but refactoring would've taken too much time.
        Hopefully, the test code will help you understand what it does.
        """
        self.timePerFrame = timePerFrame
        self._data = []
        self.segmenter = segmenter

        jumpEventSubscriber.append(self.addJumpNotice)
    
    def addVehicle(self, veHistory):
        time = max(veHistory.keys()) * self.timePerFrame

        getRatio = lambda mvBbox: mvBbox[3] / mvBbox[2] # width / height
        ratios = map(getRatio, veHistory.values())
        medianRatio = util.median(ratios)
        vehicle = "Moto" if medianRatio > 1.6 else "Automobile"
        self._data.append((time, vehicle))
        self.segmenter.addVehicle(vehicle)
    
    def addJumpNotice(self, frameIndex, **_kwargs):
        time = frameIndex * self.timePerFrame
        self._data.append((time, "<Jumping>"))
        self.segmenter.jumpToFrame(frameIndex)
    
    def getData(self):
        return self._data
    
    def tick(self):
        self.segmenter.incrementFrameIndex()



"""
Parse data obtained from analyzing the video into video count segments and write the results into an xlsx file.
"""

class SegmenterStatus(Enum):
    counting = 0
    awaitingBeginning = 1


class Segmenter:
    __slots__ = "_numberOfFramePerSegment _frameIndex _timePerFrame".split()


class DummySegmenter(Segmenter):
    def __init__(self, numberOfFramePerSegment, timePerFrame):
        self._numberOfFramePerSegment = numberOfFramePerSegment
        self._timePerFrame = timePerFrame
        self._frameIndex = 0
    
    def incrementFrameIndex(self):
        self._frameIndex += 1
    
    def jumpToFrame(self, frameIndex):
        self._frameIndex = frameIndex
    
    def addVehicle(self, vehicle):
        pass
    
    def getSegments(self):
        return []


class RealSegmenter(Segmenter):
    __slots__ = "_segments _segementDuration _currentSegment _mode".split()
    acceptedVehicleNames = "Automobile Moto".split()

    def __init__(self, numberOfFramePerSegment, timePerFrame):
        self._numberOfFramePerSegment = numberOfFramePerSegment
        self._timePerFrame = timePerFrame
        self._segementDuration = timePerFrame * numberOfFramePerSegment
        self._frameIndex = 0

        self._segments = {} # Indexed from 0
        self._mode = "Counting" # "Waiting"
        self._currentSegment = self._newSegment()

    @staticmethod
    def _newSegment():
        return {"Automobile": 0, "Moto": 0}
    
    def incrementFrameIndex(self):
        self._frameIndex += 1
        if self._frameIndex % self._numberOfFramePerSegment == 0:
            i = int(self._frameIndex / self._numberOfFramePerSegment) - 1
            if self._mode == "Counting":
                self._segments[i] = self._currentSegment
                printMV(f"Saved segment {i}.")
            self._currentSegment = self._newSegment()
            printMV(f"Starting to count for segment {i + 1}.")
            self._mode = "Counting"

        """ 
        if self._mode == "Counting":
            if self._frameIndex % self._numberOfFramePerSegment == 0:
                i = int(self._frameIndex / self._numberOfFramePerSegment)
                self._segments[i] = self._currentSegment
                self._currentSegment = self._newSegment()
        elif self._mode == "Awaiting":
            if self._frameIndex % self._numberOfFramePerSegment == 0:
                self._currentSegment = self._newSegment()
                self._mode = "Counting"
        else:
            raise RuntimeError(f"self._mode: {self._mode}") """
    
    def jumpToFrame(self, frameIndex):
        self._mode = "Awaiting"
        printMV("Awaiting")
        self._currentSegment = None
        self._frameIndex = frameIndex - 1
        self.incrementFrameIndex()
    
    def addVehicle(self, vehicleName):
        if self._mode == "Counting":
            self._currentSegment[vehicleName] += 1
        elif self._mode == "Awaiting":
            pass
    
    def getData(self):
        return [ (i, self._segementDuration * i, counts["Automobile"], counts["Moto"]) for (i, counts) in sorted(self._segments.items()) ]


def test_RealSegmenter():
    fps = 25
    rs = RealSegmenter(numberOfFramePerSegment = 4 * fps, timePerFrame = (1/fps))
    for _i in range(4):
        rs.addVehicle("Moto")
    for _j in range(7):
        rs.addVehicle("Automobile")
        rs.incrementFrameIndex()
    for _k in range(93):
        rs.incrementFrameIndex()
    firstResult = rs.getData()
    for _l in range(100):
        rs.incrementFrameIndex()
    secondResult = rs.getData()
    assert firstResult == [(0, 0.0, 7, 4),], f"firstResult: {firstResult}"
    assert secondResult == firstResult + [(1, 4.0, 0, 0),], f"secondResult: {secondResult}"