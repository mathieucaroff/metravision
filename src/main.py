import random
import sys

import cv2

from util import Namespace, printMV, printMVerr
import ihm.window as window

import parseConfig
import lecture

printMV(sys.version)

sys.path[:0] = ["src", "."]

glob = Namespace()


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

    def jumpToFrameFunction(advancementPercentage):
        lecture.jumpTo(cap, advancementPercentage)

    try:
        mvWindow = window.MvWindow(
            windowName = windowName,
            windowShape = windowShape,
            jumpToFrameFunction = jumpToFrameFunction)

        lecture.lecture(cap, mvWindow, config.raw.redCrossEnabled, glob)
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
