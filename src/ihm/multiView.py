import numpy as np
import cv2
import math

from util import Namespace

"""
Affiches un nombre arbitraire d'images ou de vidéos dans une fenêtre.
Show an arbitrary number of images or videos on window
"""
def viewDimensionsFromN(n = 1):
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

def renderNimages(imageSet, output = None, h = None, w = None):
    """
    Gather the images from the given collection into one image. All images must have the same dimension.
    If no output image buffer is given, the output dimension is that of one input image.
    Returns the output image.
    """
    imageList = imageSet.values()

    n = len(imageList)

    #Definiton of h, w depends of the choice of the user 
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
                raise ValueError("h*w est trop petit")

    if output is None:
        img = imageList[0]
        shape = list(img.shape)
        shape[2:] = [3]
        output = np.zeros(shape = shape, dtype = np.uint8)
    
    ohpx, owpx = output.shape[0:2] #pixel's number of output (same of imagList if it is not declare) It's necessary modifie to parameters defined by user

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
        else:
            raise TypeError("Unhandeled image color type.")
        

        destination = output[
            yoffset:(yoffset + imghpx),
            xoffset:(xoffset + imgwpx
        )]
        cv2.resize(
            src = image, dsize = destination.shape[:2][::-1],
            dst = destination)

        orange = (0, 116, 240)
        cv2.putText(
            img = destination, text = name, org = (16, 16),
            fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 0.6,
            color = orange, thickness = 2
        )

    return output


def setupVideoSelectionHook(mouseCallbackList):
    """
    Select and expand the video selected by double click
    """
    share = Namespace()
    share.press = False
    share.pVy = 0
    share.pVx = 0

    # mouse callback function
    def getPosition(event, x, y, flags, param):
        """
        Identify double click
        """ 
        if event == cv2.EVENT_LBUTTONDBLCLK:
            share.press = True
            share.pVy = y
            share.pVx = x
    

    mouseCallbackList.append(getPosition)

    displayedImageNameList = []

    def updateWindows(imageSet, windowShape):
        imageNameList, _ = zip(*imageSet.items())

        if share.press == True:
            n = len(imageSet)
            h, w = viewDimensionsFromN(n)

            width, height = windowShape
            imghpx = height // h
            imgwpx = width // w
            i = math.floor(share.pVy / imghpx)
            j = math.floor(share.pVx / imgwpx)
            m = j + i*w
            if m < n:
                displayedImageNameList.append(imageNameList[m])
            
            share.press = False
        
        for imageName in displayedImageNameList:
            cv2.imshow(imageName, imageSet[imageName])


    return updateWindows