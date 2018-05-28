from enum import Enum

import util

class AnalyseData:
    def __init__(self, timePerFrame, jumpEventSubscriber):
        self.timePerFrame = timePerFrame
        self._data = []

        jumpEventSubscriber.append(self.addJumpNotice)
    
    def addVehicle(self, veHistory):
        time = max(veHistory.keys()) * self.timePerFrame

        getRatio = lambda mvBbox: mvBbox[3] / mvBbox[2] # width / height
        ratios = map(getRatio, veHistory.values())
        medianRatio = util.median(ratios)
        vehicle = "Moto" if medianRatio > 1.6 else "Automobile"
        self._data.append((time, vehicle))
    
    def addJumpNotice(self, frameIndex, **_kwargs):
        time = frameIndex * self.timePerFrame
        self._data.append((time, "<Jumping>"))
    
    def getData(self):
        return self._data



"""
Parse data obtained from analyzing the video into video count segments and write the results into an xlsx file.
"""


class SegmenterStatus(Enum):
    counting = 0
    awaitingBeginning = 1


class Segmenter:
    def __init__(self, vehiclesInformations, segmentDuration):
        self.vehiclesInformations = vehiclesInformations
        self.segmentDuration = segmentDuration
    


def segmenting(vehiclesInformations, segmentDuration, timeOffset = 0):
    """
    Takes a list of recognised vehicles and for each, counts them into segments using the given groups.
    Counts nothing until the first jump notification is met.
    
    timeOffset is subtracted from all times when determining the indexes of the segments.
    Nothing is counted before timeOffset.
    """
    segments = dict()

    viIterator = iter(vehiclesInformations)

    oldSegmentIndex = 0
    status = SegmenterStatus.awaitingBeginning
    currentSegmentVehicleCounts = dict()
    try:
        while True:
            vtime, vehicleName = next(viIterator)
            segmentIndex = int((vtime - timeOffset) // segmentDuration)
            changingOfSegment = (segmentIndex != oldSegmentIndex)
            jumping = (vehicleName == "<Jumping>")

            if changingOfSegment and not jumping:
                if status == SegmenterStatus.awaitingBeginning:
                    status = SegmenterStatus.counting
                    currentSegmentVehicleCounts = dict()
                elif status == SegmenterStatus.counting:
                    for i in range(oldSegmentIndex, segmentIndex):
                        segments[i] = currentSegmentVehicleCounts
                        currentSegmentVehicleCounts = dict()
                else:
                    raise ValueError()

            if jumping:
                status = SegmenterStatus.awaitingBeginning

            if status == SegmenterStatus.counting and not jumping:
                currentSegmentVehicleCounts[vehicleName] = currentSegmentVehicleCounts.get(vehicleName, 0) + 1

            oldSegmentIndex = segmentIndex
    except StopIteration:
        pass

    segmentList = sorted(segments.items())

    results = []

    for segmentIndex, countDict in segmentList:
        assert len(countDict.keys()) <= 2, f"<=2: len: {len(countDict.keys())} ::: {countDict.keys()}"
        i = segmentIndex
        if i < 0:
            continue
        t = i * segmentDuration + timeOffset
        auto = countDict.get("Automobile", 0)
        moto = countDict.get("Moto", 0)
        results.append([i, t, auto, moto])

    return results
