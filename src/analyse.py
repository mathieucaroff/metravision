import cv2
import numpy as np

import util
from util import printMV


def setupAnalyseTools():
    # Background subtractor initialisation
    bgSub = cv2.createBackgroundSubtractorMOG2()

    # blobDetector initialisation
    params = cv2.SimpleBlobDetector_Params()
    params.minDistBetweenBlobs = 4
    params.filterByArea = True
    params.minArea = 4_000
    params.maxArea = 100_000
    params.filterByInertia = True
    params.maxInertiaRatio = 2
    blobDetector = cv2.SimpleBlobDetector_create(params)

    def mvTrackerCreator():
        tracker_type = 'KCF'
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':# Bugged
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'CSRT':
            tracker = cv2.TrackerCSRT_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        return tracker

    return bgSub, blobDetector, mvTrackerCreator



def analyse(bgSub, blobDetector, mvTrackerCreator, trackerList, im, last_fgMask, oneBeforeLast_fgMask, glob):
    #shape = im["frame"][:2]
    sub = bgSub.apply(image = im["frame"]) #, learningRate = 0.05)
    im["fgMask"] = sub
    #if sub is not None:
    #    im["fgMask"] = sub
    #elif "fgMask" in im:
    #    pass
    #else:
    #    im["fgMask"] = cv2.cvtColor(im["frame"], cv2.COLOR_GRAY2BGR)


    
    # Two-frame bitwise AND
    im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], last_fgMask, oneBeforeLast_fgMask)
    #try:
    #    im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], last_fgMask, oneBeforeLast_fgMask)
    #except cv2.error:
    #    im["bitwise_fgMask_and"] = np.zeros(shape = shape, dtype = np.uint8)

    # erodeAndDilate
    mask = erodeAndDilate(im)

    # Contour
    contour(im, mask)

    # Blob Detector
    frame = im["dilateC"]
    blobKeypoints = blobDetection(blobDetector, im, frame = frame)

    # Tracking
    frame = im["blob_dilateC"]
    mvTracking(mvTrackerCreator, im, frame, blobKeypoints, trackerList, glob)

    return trackerList


def erodeAndDilate(im):
    """
    Erode et Dilate l'image plusieurs fois.
    """
    mask = im["bitwise_fgMask_and"]

    erodeA = 4
    dilateA = 20
    erodeB = 26
    dilateB = 15 # previously erodeA + erodeB - dilateA
    dilateC = 20

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


def blobDetection(blobDetector, im, frame):
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
    blobKeypoints = blobDetector.detect(255 - frame)
    return blobKeypoints


def mvTracking(mvTrackerCreator, im, frame, blobKeypoints, trackerList, glob):
    # Update trakers
    for mvTracker in trackerList:
        mvTracker.ret, mvTracker.bbox = mvTracker.tracker.update(frame) # Error ?
        green = (0, 255, 0)
        showTracker(im["frame"], mvTracker, green)

    # Debug code
    try:
        l = len(glob.trackerList)
    except AttributeError:
        l = 0
    if len(trackerList) > l:
        glob.trackerList = trackerList
    
    # bbox: Bounding Box
    # Add new trakers for blobs whose keypoint location isn't inside a tracker bbox.
    for blob in blobKeypoints:
        if any(util.pointInBbox(blob.pt, mvTracker.bbox) for mvTracker in trackerList):
            continue # Do not create a tracker = continue to next iteration
        # Get and draw bbox:
        bbox = util.bboxFromKeypoint(blob, width_on_height_ratio = 0.5)
        blue = (255, 0, 0)

        # Create and register tracker:
        mvTracker = util.Namespace()
        mvTracker.tracker = mvTrackerCreator()
        mvTracker.tracker.init(frame, bbox)
        mvTracker.ret = True
        mvTracker.bbox = bbox
        blue = (255, 0, 0)
        showTracker(im["frame"], mvTracker, blue)
        trackerList.append(mvTracker)

def showTracker(frame, mvTracker, color):
    cv2.rectangle(frame, *util.pointsFromBbox(mvTracker.bbox), color, thickness = 6)