import numpy as np
import cv2
import math
"""
Affiches un nombre arbitraire d'images ou de vidéos dans une fenêtre.
Show an arbitrary number of images or videos on window
"""
# TODO
h = 0
w = 0
def viewDimensionsFromN(n = 1):
    """
    Compute the number of horizontal and vertical views needed to reach at least n views.
    Returns a pair of numbers.
    """
    global h, w
    while True:
        if h * w >=n:
            break
        h += 1
        if h * w >= n:
            break
        w += 1
    return (h, w)

def renderNimages(imageList, output = None, h = None, w = None):
    """
    Gather the images from the given collection into one image. All images must have the same dimension.
    If no output image buffer is given, the output dimension is that of one input image.
    Returns the output image.
    """
    imageList = list(imageList)

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


def selectVideo(imageList, output):
    """
    Select and expand the video selected by double click
    """
    press = False
    pVy = 0
    pVx = 0

    imageList = list(imageList)
    n = len(imageList)
    h, w = viewDimensionsFromN(n)
    ohpx, owpx = output.shape[0:2]
    imghpx = ohpx // h
    imgwpx = owpx // w

    # mouse callback function
    def getPosition(event,x,y,flags,param):
        """
        Identify double click
        """ 
        if event == cv2.EVENT_LBUTTONDBLCLK:
            press = True
            pVy = y
            pVx = x
    
    
    cv2.setMouseCallback('Metravision', getPosition)   
    if press == True:
        i = math.ceil(pVy / imghpx)
        j = math.ceil(pVx / imgwpx)
        m = j + i*w

        videoSelected = imageList[m]
        
        cv2.namedWindow('Selected')
        while (1):
            cv2.imshow('Selected', videoSelected)
            if cv2.waitKey(1) & 0xFF == ord('x'):
                break
            cv2.destroyAllWindows()

        press == False

        #return videoSelected