import random
import sys

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
    with open("metravision.config.yml") as configFile:
        config = parseConfig.MvConfig.fromConfigFile(configFile)

    windowName = config.raw.windowName
    windowHeight = config.raw["window"]["height"]
    windowWidth = config.raw["window"]["width"]
    windowShape = (windowHeight, windowWidth)

    videoPath = random.choice(config.video.files)
    try:
        open(videoPath).close()
    except FileNotFoundError:
        printMVerr(f"The specified video {videoPath} coudln't be open. (Missing file?)")
        raise

    cap = cv2.VideoCapture(videoPath)

    try:
        lecteur = lecture.Lecteur(cap, config.raw.redCrossEnabled, debug)

        mvWindow = window.MvWindow(
            windowName = windowName,
            windowShape = windowShape,
            playbackStatus = lecteur.playbackStatus,
            jumpToFrameFunction = lecteur.jumpTo)

        with util.neutralContextManager():
        # with util.interactOnExceptionEnabled():
        # with util.pdbPostMortem():
            lecteur.run(mvWindow)
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
