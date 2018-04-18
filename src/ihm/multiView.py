import numpy as np
import cv2
"""
Affiches un nombre arbitraire d'images ou de vidéos dans une fenêtre.
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

def renderNimages(imageSet, output = None, viewDimensions = None, fillMode = "fill"):
    """
    Gather the images from the given collection into one image. All images must have the same dimension.
    If no output image buffer is given, the output dimension is that of one input image.
    Returns the output image.
    """
    imageNameList, imageList = zip(*imageSet.items())

    n = len(imageList)
    if viewDimensions is None:
        viewDimensions = viewDimensionsFromN(n)
    h, w = viewDimensions

    if output is None:
        img = imageList[0]
        shape = list(img.shape)
        shape[2:] = [3]
        output = np.zeros(shape = shape, dtype = np.uint8)
    
    ohpx, owpx = output.shape[0:2] #pixel's number of output (same of imagList if it is not declare)

    imghpx = ohpx // h
    imgwpx = owpx // w

    for m in range(n):
        i = m // w
        j = m % w
        yoffset = i * imghpx
        xoffset = j * imgwpx

        currentImage = imageList[m]

        if len(currentImage.shape) == 2 and currentImage.dtype == np.uint8:
            currentImage = cv2.cvtColor(currentImage, cv2.COLOR_GRAY2BGR)
        elif len(currentImage.shape) == 3 and currentImage.dtype == np.uint8:
            pass
        else:
            raise TypeError("Unhandeled image color type.")

        destination = output[yoffset:(yoffset + imghpx), xoffset:(xoffset + imgwpx)]
        cv2.resize(src = currentImage, dsize = destination.shape[:2][::-1], dst = destination)

    return output