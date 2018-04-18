import cv2
import numpy as np


def setupAnalyseTools():
    # Background subtractor initialisation
    bgSub = cv2.createBackgroundSubtractorMOG2()

    # blobDetector initialisation
    params = cv2.SimpleBlobDetector_Params()
    params.minDistBetweenBlobs = 4
    params.filterByArea = True
    params.minArea = 800
    params.maxArea = 100_000
    params.filterByInertia = True
    params.maxInertiaRatio = 2
    blobDetector = cv2.SimpleBlobDetector_create(params)
    return bgSub, blobDetector


def analyse(bgSub, blobDetector, im, last_fgMask, oneBeforeLast_fgMask):
    im["fgMask"] = bgSub.apply(image = im["frame"]) #, learningRate = 0.05)

    # Two-frame and
    try:
        im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], last_fgMask, oneBeforeLast_fgMask)
    except cv2.error:
        im["bitwise_fgMask_and"] = np.zeros(shape = im["fgMask"].shape, dtype = np.uint8)

    # erodeAndDilate
    mask = erodeAndDilate(im)

    # Contour
    # contour(im, mask)

    # Blob Detector
    blobDetection(blobDetector, im)


def erodeAndDilate(im):
    """
    Erode et Dilate l'image plusieurs fois.
    """
    mask = im["bitwise_fgMask_and"]

    erodeA = 4
    dilateA = 20
    erodeB = 26
    dilateB = 15 # previously erodeA + erodeB - dilateA
    dilateC = 4

    mask = cv2.erode(mask, easyKernel(erodeA))
    im["erodeMaskA"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateA))
    im["dilateMaskA"] = mask

    mask = cv2.erode(mask, easyKernel(erodeB))
    im["erodeMaskB"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateB))
    im["dilateMaskB"] = mask

    # edMask = mask

    mask = cv2.bitwise_and(mask, im["fgMask"])
    im["bitwise_fgMask_dilateB_and"] = mask

    mask = cv2.dilate(mask, easyKernel(dilateC))
    im["dilateC"] = mask

    # cv2.cvtColor(im["dilateMaskB"], cv2.COLOR_GRAY2BGR)
    return mask

def easyKernel(size, sizeX = None):
    """Generate an OpenCV kernel objet of given size.
    Note: I haven't checked the sizeX parameter"""
    sizeY = size
    if sizeX is None:
        sizeX = size
    return cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (sizeY, sizeX) )


def contour(im, mask):
    """
    Detect les contours dans l'image et les dessine.
    """
    red = (0, 0, 255)

    img, contourPointList, hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    im["dilateMaskA"] = cv2.cvtColor(im["dilateMaskA"], cv2.COLOR_GRAY2BGR)

    allContours = -1
    cv2.drawContours(
        image = im["dilateMaskA"],
        contours = contourPointList,
        contourIdx = allContours,
        color = red
    )


def blobDetection(blobDetector, im):
    red = (0, 0, 255)
    imageNameList = list(im.keys()) # Buffered
    for imageName in imageNameList:
        if not "dilate" in imageName:
            continue
        blobKeypoints = blobDetector.detect(255 - im[imageName])
        im[f"blob_{imageName}"] = cv2.drawKeypoints(
            image = im[imageName],
            keypoints = blobKeypoints,
            outImage = np.array([]),
            color = red,
            flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )

