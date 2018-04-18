import cv2
import numpy as np

from ihm.multiView import renderNimages
from ihm.progressBar import drawBar

from util import Namespace

def window(im, advancementPercentage):
    # Display the resulting frame
    height = 800
    width = 960
    shape = (height, width, 3)
    output = np.zeros(shape = shape, dtype = np.uint8)
    barProperties = Namespace()
    barProperties.bgCol = [255, 255, 255]
    barProperties.fgCol = [255, 191, 127]
    barProperties.height = 30

    #: viewSet = im
    renderNimages(im, output = output[:-barProperties.height])
    drawBar(barProperties, buffer = output, advancementPercentage = advancementPercentage)
    cv2.imshow("Metravision", output)


def waitkey(controlledTime):
    continuing = "continue"
    if cv2.waitKey(max(0, int(1000 * controlledTime)) + 1) & 0xFF == ord('q'):
        continuing = "break"
    if windowClosed("Metravision"):
        continuing = "break"
    return continuing


def windowClosed(windowName):
    """Checking for a property of the window to tell whether it is (still) open."""
    return cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) != 1
