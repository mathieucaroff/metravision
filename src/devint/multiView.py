"""
Affiches un nombre arbitraire d'images ou de vidéos dans une fenêtre.
Show an arbitrary number of images or videos on window
"""

import numpy as np
import cv2
import math

from util import Namespace

def viewDimensionsFromN(n=1):
    """
    Compute the number of horizontal and vertical views needed to reach at least n views.
    Returns a pair of numbers.
    """
    h = 0
    w = 0
    while True:
        if h * w >=n:
            break
        h += 1
        if h * w >= n:
            break
        w += 1
    return (h, w)

def renderNimages(multiViewConfig, videoName, imageSet, output=None, h=None, w=None):
    """
    Gather the images from the given collection into one image. All images must have the same dimension.
    If no output image buffer is given, the output dimension is that of one input image.
    Returns the output image.
    """
    imageList = imageSet.values()

    n = max(len(imageList), multiViewConfig.viewNumber)

    # Definition of h, w depends of the choice of the user 
    if h is None:
        if w is None:
            h, w = viewDimensionsFromN(n)
        else:
            h = math.ceil(n / w)
    else:
        if w is None:
            w = math.ceil(n / h)
        else:
            if not h * w >= n:
                raise ValueError("h * w est trop petit")

    if output is None:
        img = imageList[0]
        shape = list(img.shape)
        shape[2:] = [3]
        output = np.zeros(shape=shape, dtype=np.uint8)
    
    ohpx, owpx = output.shape[0:2] #pixel's number of output (same as imageList if it is not declare) It's necessary modifie to parameters defined by user

    imghpx = ohpx // h
    imgwpx = owpx // w

    for m, (name, image) in enumerate(imageSet.items()):
        i = m // w
        j = m % w
        yoffset = i * imghpx
        xoffset = j * imgwpx

        if len(image.shape) == 2 and image.dtype == np.uint8:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif len(image.shape) == 3 and image.dtype == np.uint8:
            pass
        elif len(image.shape) == 3 and image.dtype == np.float32:
            pass
        else:
            raise TypeError("Unhandeled image color type.")
        

        destination = output[
            yoffset:(yoffset + imghpx),
            xoffset:(xoffset + imgwpx),
        ]
        cv2.resize(
            src=image,
            dsize=destination.shape[:2][::-1],
            dst=destination,
        )
        
        if name == "frame":
            name = videoName
        
        orange = (0, 128, 256)
        cv2.putText(
            img=destination,
            text=name,
            org=(16, 16),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.6,
            color=orange,
            thickness=2,
        )

    return output


def setupVideoSelectionHook(multiViewConfig, mouseCallbackList, displayShape, playbackStatus, windowClosed):
    """
    Select and expand the video selected by double click
    """
    height, width = displayShape
    share = Namespace()
    share.press = False
    share.pVy = 0
    share.pVx = 0

    openEvent = multiViewConfig.openEvent

    # mouse callback function
    def getPosition(event, x, y, flags, param):
        """
        Catch the click if it is enabled.
        """
        _ = flags, param
        click = False
        click |= openEvent.click and event == cv2.EVENT_LBUTTONUP
        click |= openEvent.doubleClick and event == cv2.EVENT_LBUTTONDBLCLK
        if click:
            share.press = True
            share.pVy = y
            share.pVx = x
            playbackStatus.refreshNeeded = True
    
    mouseCallbackList.append(getPosition)

    displayedImageNameList = []
    displayedImageNameListAdd = []

    def updateSubWindows(imageSet):
        imageNameList, _ = zip(*imageSet.items())
        
        for imageName in list(displayedImageNameList):
            if windowClosed(imageName):
                displayedImageNameList.remove(imageName)
            else:
                if imageName in imageSet:
                    cv2.imshow(imageName, imageSet[imageName])

        if share.press == True:
            n = max(len(imageSet), multiViewConfig.viewNumber)
            h, w = viewDimensionsFromN(n)

            imghpx = height // h
            imgwpx = width // w
            i = math.floor(share.pVy / imghpx)
            j = math.floor(share.pVx / imgwpx)
            m = j + i*w
            if m < n:
                imageName = imageNameList[m]
                if imageName not in displayedImageNameList:
                    displayedImageNameListAdd.append(imageName)
            
            share.press = False
        
        for imageName in displayedImageNameListAdd:
            cv2.imshow(imageName, imageSet[imageName])
        displayedImageNameList.extend(displayedImageNameListAdd)
        displayedImageNameListAdd[:] = []

    return updateSubWindows