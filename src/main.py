import random
import sys
from pprint import pprint

from pathlib import Path

import cv2
import numpy as np

from util import printMV, printMVerr
import util
import ihm.window as window

import parseConfig
import lecture
import perspective
import fileresults

printMV("Versions:")
printMV(f"[Python] {sys.version}")
printMV(f"[Numpy] {np.__version__}")
printMV(f"[OpenCV] {cv2.__version__}")

sys.path[:0] = ["src", "."]

def main():
    for x in list(range(3)) + [0]:
        p = Path("../" * x + "metravision.config.yml")
        if p.is_file():
            with p.open() as configFile:
                config = parseConfig.MvConfig.fromConfigFile(configFile)
            break
    else:
        p.open().close() # raise FileNotFoundError

    windowName = config.raw.windowName
    windowHeight = config.raw["window"]["height"]
    windowWidth = config.raw["window"]["width"]
    windowShape = (windowHeight, windowWidth)



    if config.raw.usePerspectiveCorrection:
        pInfo = config.raw.videoPerspectiveInformation
        filesWithPerspectiveInformation = [path for path in config.video.files if any(pattern in path for pattern in pInfo.keys())]
        videoPath = Path(random.choice(filesWithPerspectiveInformation))

        firstOf = next
        vpInfo = firstOf(info for (patternKey, info) in pInfo.items() if patternKey in str(videoPath))
        
        perspectiveCorrector = perspective.PerspectiveCorrector(
            xLeftEdge = vpInfo["xLeftEdge"],
            xRightEdge = vpInfo["xRightEdge"],
            vanishingPoint = vpInfo["vanishingPoint"])
    else:
        videoPath = Path(random.choice(config.video.files))
        perspectiveCorrector = perspective.DummyPerspectiveCorrector()

    videoName = videoPath.name

    try:
        videoPath.open().close()
    except FileNotFoundError:
        printMVerr(f"The specified video {videoPath} coudln't be open. (Missing file?)")
        raise

    cap = cv2.VideoCapture(str(videoPath))

    try:
        lecteur = lecture.Lecteur(
            cap = cap,
            redCrossEnabled = config.raw.redCrossEnabled,
            perspectiveCorrector = perspectiveCorrector)

        mvWindow = window.MvWindow(
            windowName = windowName,
            windowShape = windowShape,
            videoName = videoName,
            playbackStatus = lecteur.playbackStatus,
            jumpToFrameFunction = lecteur.jumpTo)

        with util.neutralContextManager():
        # with util.interactOnExceptionEnabled():
        # with util.pdbPostMortem():
            lecteur.run(mvWindow)
        # print(lecteur.getData())


        data = lecteur.getData()

        assert type(data) == list
        fileresults.writeFile(data)
        
        pprint(lecteur.getData())

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
