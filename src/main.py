import random
import sys
from pprint import pprint

from pathlib import Path

import cv2
import numpy as np

from util import Namespace, printMV, printMVerr
import util
import ihm.window as window

import parseConfig
import lecture

printMV("Versions:")
printMV(f"[Python] {sys.version}")
printMV(f"[Numpy] {np.__version__}")
printMV(f"[OpenCV] {cv2.__version__}")

sys.path[:0] = ["src", "."]

debug = Namespace()


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

    videoPath = Path(random.choice(config.video.files))
    videoName = videoPath.name

    try:
        videoPath.open().close()
    except FileNotFoundError:
        printMVerr(f"The specified video {videoPath} coudln't be open. (Missing file?)")
        raise

    cap = cv2.VideoCapture(str(videoPath))

    try:
        lecteur = lecture.Lecteur(cap, config.raw.redCrossEnabled, debug)

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
        pprint(lecteur.getData())
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
