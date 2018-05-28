from enum import Enum

from pathlib import Path

from openpyxl import Workbook


import util

import os, sys
util.printMV(os.path.basename(__file__), "<><>", sys.path)

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


def genResultFileName(videoFileName, ext):
    prefixStr = "Mvs-results"

    if util.developementMode == True:
        from datetime import datetime
        with Path("VERSION.txt").open() as f:
            version = [kStr for kStr in f.readlines()[0].split(".")]
        versionStr = "-".join(version)
        timeStr = datetime.utcnow().strftime("%Y-%m-%dT%HZ")
        prefixStr = f"{prefixStr}--{versionStr}--{timeStr}"

    videoFileNameStr = "-".join(videoFileName.split("."))

    return f"{prefixStr}--{videoFileNameStr}.{ext}"



def createXLS(sheetContent, sheetHeader = None):
    wb = Workbook()
    ws = wb.active
    if sheetHeader is not None:
        #for i, val in enumerate(sheetHeader):
        #    ws.cell(row = 1, column = i).value = val
        _hasHeader = 1
        sheetContent[:0] = [sheetHeader]
    else:
        _hasHeader = 0
    
    for i, rowContent in enumerate(sheetContent):
        #util.show(rowContent = rowContent)
        for j, val in enumerate(rowContent):
            #util.show(val = val)
            ws.cell(row = i + 1, column = j + 1).value = val
    return wb


"""
def cleanCells(destFile)
    "Clear all file's cells"
    wb = Workbook()
    ws = wb.active
    if ws['A1'] is not None:
"""
def writeFile(fileData):
    wb = Workbook()
    # grab the active worksheet
    ws = wb.active
    i=0
    print(len(fileData))
    for i, par in enumerate(fileData):
        ws.cell(row=i+1, column=1).value = par[0]
        ws.cell(row=i+1, column=2).value = par[1]
    
    # Save the file
    wb.save("results.xlsx")