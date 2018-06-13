"""
The file main is the entry point of Metravision. It reads the configuration and starts the other modules.
"""

# Python utils
#from distutils.version import StrictVersion

# Python io modules
import random
import sys
from pathlib import Path
import logging


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

logging.basicConfig(level=0)

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
    

    logger = logging.getLogger("[MV]")

    # https://docs.python.org/3/howto/logging.html#configuring-logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False

    if config.raw.developerMode and not config.raw.backgroundMode:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")


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

    try:
        if len(sys.argv) > 1:
            printMV("argv", sys.argv)
            for videoLocation in sys.argv[1:]:
                videoPath = Path(videoLocation)
                playbackStatus = lecture.PlaybackStatus(play = True)
                processVideo(logger, redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath, playbackStatus)
                if playbackStatus.quitting:
                    break
        elif backgroundMode:
            for videoLocation in config.backgroundVideo.files:
                videoPath = Path(videoLocation)
                playbackStatus = lecture.PlaybackStatus(play = True)
                processVideo(logger, redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath, playbackStatus)
                if playbackStatus.quitting:
                    break
        else:
            videoPath = Path(random.choice(config.video.files))
            playbackStatus = lecture.PlaybackStatus(play = True)
            processVideo(logger, redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath, playbackStatus)
    finally:
        cv2.destroyAllWindows()

    pt = "printTimes"
    if pt in config.raw and config.raw[pt] == True:
        printMV("[:Recorded times totals:]")
        for fname in util.timed.functionIndex:
            time = getattr(util.timed, fname)
            printMV("Function {fname} ::: {time:.04} seconds".format(fname = fname, time = time))


def processVideo(logger, redCrossEnabled, resultPathTemplate, backgroundMode, windowName, windowShape, videoPath, playbackStatus):

    videoName = videoPath.name
    logger.info(f"Starting to process video `{videoName}`")

    if not videoPath.is_file():
        raise FileNotFoundError(f"The specified video `{videoPath}` coudln't be open. (Missing file?)")

    cap = cv2.VideoCapture(str(videoPath))

    try:
        lecteur = lecture.Lecteur(
            logger = logger,
            cap = cap,
            redCrossEnabled = redCrossEnabled,
            playbackStatus = playbackStatus)

        if backgroundMode:
            lecteur.jumpTo(0)
        else:
            lecteur.jumpTo(0) # (random.random() * 3 / 4)

        mvWindow = window.MvWindow(
            logger = logger,
            windowName = windowName,
            windowShape = windowShape,
            videoName = videoName,
            backgroundMode = backgroundMode,
            playbackStatus = lecteur.playbackStatus,
            jumpToFrameFunction = lecteur.jumpTo)

        with util.pdbPostMortemUpon(util.DeveloperInterruption):
            lecteur.run(mvWindow)

        if playbackStatus.endReached:
            logger.info(f"Finished video `{videoName}`")

        # -------

        ### Getting data and writing results
        results = lecteur.getData()
        def saveResultAsXlsx(results):
            segmentIndexList = [ v[0] for v in results ]

            resultFilePath = fileresults.fillPathTemplate(videoPath = videoPath, ext = "xlsx", pathTemplate = resultPathTemplate, segmentIndexList = segmentIndexList)
            Path(resultFilePath).absolute().parent.mkdir(parents = True, exist_ok = True)

            xlsdoc = fileresults.createXLS(results, sheetHeader = ["Index", "Time", "Automobiles", "Motos"])
            xlsdoc.save(resultFilePath)
            logger.info(f"Wrote file `{resultFilePath}`")
        saveResultAsXlsx(results)

    finally:
        # When everything done, release the capture
        cap.release()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception: # pylint: disable=broad-except
        traceback.print_exc()
        inp = input()
        if inp and inp[0] in "dp":
            import pdb
            pdb.post_mortem()
