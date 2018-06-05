"""
The file main is the entry point of Metravision. It reads the configuration and starts the other modules.
"""

# Python utils
#from distutils.version import StrictVersion

# Python io modules
import random
import sys
from pathlib import Path


# Dependencies
import cv2
import numpy as np


# Metravision modules
from util import printMV
import util
import devint.window as window

import parseConfig
import lecture
#import perspective
import fileresults


printMV("Versions:")
printMV(f"[Python]      {sys.version}")
printMV(f"[Numpy]       {np.__version__}")
printMV(f"[OpenCV]      {cv2.__version__}")
__version__ = Path("VERSION.txt").read_text()
printMV(f"[Metravision] {__version__}")

# Developper versions:
"""Conda on Linux
[MV] Versions:
[MV] [Python]      3.6.4 |Anaconda, Inc.| (default, Jan 16 2018, 18:10:19)
[GCC 7.2.0]
[MV] [Numpy]       1.14.3
[MV] [OpenCV]      3.4.1
[MV] [Metravision] 1.0.1
"""


def main():
    for x in list(range(3)) + [0]:
        p = Path("../" * x + "metravision.config.yml")
        if p.is_file():
            with p.open() as configFile:
                config = parseConfig.MvConfig.fromConfigFile(configFile, version="1.0.4")
            break
    else:
        p.open().close() # raise FileNotFoundError

    windowName = config.raw.windowName
    windowHeight = config.raw.window.height #raw["window"]["height"]
    windowWidth =  config.raw.window.width  #raw["window"]["width"]
    windowShape = (windowHeight, windowWidth)
    
    backgroundMode = config.raw.backgroundMode
    
    templates = config.raw.resultDestinationTemplates
    if config.raw.developerMode == True:
        templates = templates.developer
    resultPathTemplate = templates.counts

    redCrossEnabled = config.raw.redCrossEnabled

    if backgroundMode:
        for videoLocation in config.backgroundVideo.files:
            videoPath = Path(videoLocation)
            processVideo(redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath)
    else:
        videoPath = Path(random.choice(config.video.files))
        processVideo(redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath)


def processVideo(redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath):

    videoName = videoPath.name

    if not videoPath.is_file():
        raise FileNotFoundError(f"The specified video {videoPath} coudln't be open. (Missing file?)")

    cap = cv2.VideoCapture(str(videoPath))

    try:
        lecteur = lecture.Lecteur(
            cap = cap,
            redCrossEnabled = redCrossEnabled)

        if backgroundMode:
            lecteur.jumpTo(0)
        else:
            lecteur.jumpTo(2 / 3) # (random.random() * 3 / 4)

        mvWindow = window.MvWindow(
            windowName = windowName,
            windowShape = windowShape,
            videoName = videoName,
            backgroundMode = backgroundMode,
            playbackStatus = lecteur.playbackStatus,
            jumpToFrameFunction = lecteur.jumpTo)

        # with util.neutralContextManager():
        # with util.interactPostMortemUpon():
        with util.pdbPostMortemUpon(Exception):
            with util.pdbPostMortemUpon(util.DeveloperInterruption):
                lecteur.run(mvWindow)
        # print(lecteur.getData())

        # -------

        ### Getting data and writing results
        results = lecteur.getData()
        segmentIndexList = [ v[0] for v in results ]

        resultFilePath = fileresults.fillPathTemplate(videoPath = videoPath, ext = "xlsx", pathTemplate = resultPathTemplate, segmentIndexList = segmentIndexList)
        Path(resultFilePath).absolute().parent.mkdir(parents = True, exist_ok = True)

        xlsdoc = fileresults.createXLS(results, sheetHeader = ["Index", "Time", "Automobiles", "Motos"])
        xlsdoc.save(resultFilePath)

        printMV("[:Recorded times totals:]")
        for fname in util.timed.functionIndex:
            time = getattr(util.timed, fname)
            printMV("Function {fname} ::: {time:.04} seconds".format(fname = fname, time = time))

    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception: # pylint: disable=broad-except
        traceback.print_exc()
        input()
