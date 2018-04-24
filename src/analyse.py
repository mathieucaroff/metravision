import cv2
import numpy as np

import util
from util import printMV

class AnalyseTool():
    # Setup:
    def __init__(self):
        # Background subtractor initialisation
        self.bgSub = cv2.createBackgroundSubtractorMOG2()

        # blobDetector initialisation
        params = cv2.SimpleBlobDetector_Params()
        params.minDistBetweenBlobs = 4
        params.filterByArea = True
        params.minArea = 4_000
        params.maxArea = 100_000
        params.filterByInertia = True
        params.maxInertiaRatio = 2
        self.blobDetector = cv2.SimpleBlobDetector_create(params)

    @staticmethod
    def mvTrackerCreator():
        """
            Crée et renvoie un tracker du type spécifié par la variable.
        """
        tracker_type = 'KCF'

        tracker_create = {
            "BOOSTING": cv2.TrackerBoosting_create,
            "MIL": cv2.TrackerMIL_create,
            "KCF": cv2.TrackerKCF_create,
            "TLD": cv2.TrackerTLD_create,
            "MEDIANFLOW": cv2.TrackerMedianFlow_create,
            "GOTURN": cv2.TrackerGOTURN_create,
            "CSRT": cv2.TrackerCSRT_create,
            "MOSSE": cv2.TrackerMOSSE_create,
        }[tracker_type]

        tracker = tracker_create()

        return tracker


    # Run:
    def run(self, trackerList, im, last_fgMask, oneBeforeLast_fgMask, glob):
        # sub = self.bgSub.apply(image = im["frame"]) #, learningRate = 0.05)
        # im["fgMask"] = sub
        im["fgMask"] = im["frame"]

        # Two-frame bitwise AND
        # im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], last_fgMask, oneBeforeLast_fgMask)

        # erodeAndDilate
        # mask = self.erodeAndDilate(im)

        # Contour
        #self.contour(im, mask)

        # Blob Detector
        #frame = im["dilateC"]
        #blobKeypoints = self.blobDetection(im, frame = frame)

        # Tracking
        #frame = im["blob_dilateC"]
        #self.mvTracking(im, frame, blobKeypoints, trackerList, glob)

        return trackerList

    @classmethod
    def erodeAndDilate(cls, im):
        """
        Erode et Dilate l'image plusieurs fois.
        """
        mask = im["bitwise_fgMask_and"]

        erodeA = 4
        dilateA = 20
        erodeB = 26
        dilateB = 15 # previously erodeA + erodeB - dilateA
        dilateC = 20

        mask = cv2.erode(mask, cls.easyKernel(erodeA))
        im["erodeMaskA"] = mask

        mask = cv2.dilate(mask, cls.easyKernel(dilateA))
        im["dilateMaskA"] = mask

        mask = cv2.erode(mask, cls.easyKernel(erodeB))
        im["erodeMaskB"] = mask

        mask = cv2.dilate(mask, cls.easyKernel(dilateB))
        im["dilateMaskB"] = mask

        # edMask = mask

        mask = cv2.bitwise_and(mask, im["fgMask"])
        im["bitwise_fgMask_dilateB_and"] = mask

        mask = cv2.dilate(mask, cls.easyKernel(dilateC))
        im["dilateC"] = mask

        # cv2.cvtColor(im["dilateMaskB"], cv2.COLOR_GRAY2BGR)
        return mask

    @staticmethod
    def easyKernel(size, sizeX = None):
        """Generate an OpenCV kernel objet of given size.
        Note: I haven't checked the sizeX parameter"""
        sizeY = size
        if sizeX is None:
            sizeX = size
        return cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (sizeY, sizeX) )

    @staticmethod
    def contour(im, mask):
        """
        Detect les contours dans l'image et les dessine.
        """
        red = (0, 0, 255)

        img, contourPointList, hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        _, _ = img, hierachy # pylint~

        im["dilateMaskA"] = cv2.cvtColor(im["dilateMaskA"], cv2.COLOR_GRAY2BGR)

        allContours = -1
        cv2.drawContours(
            image = im["dilateMaskA"],
            contours = contourPointList,
            contourIdx = allContours,
            color = red
        )


    def blobDetection(self, im, frame):
        red = (0, 0, 255)
        imageNameList = list(im.keys()) # Buffered
        for imageName in imageNameList:
            if not "dilate" in imageName:
                continue
            blobKeypoints = self.blobDetector.detect(255 - im[imageName])
            im[f"blob_{imageName}"] = cv2.drawKeypoints(
                image = im[imageName],
                keypoints = blobKeypoints,
                outImage = np.array([]),
                color = red,
                flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
            )
        blobKeypoints = self.blobDetector.detect(255 - frame)
        return blobKeypoints


    def mvTracking(self, im, frame, blobKeypoints, trackerList, glob):
        # Update trakers
        for i, mvTracker in enumerate(trackerList):
            mvTracker.ret, mvTracker.bbox = mvTracker.tracker.update(frame) # Error ?
            green = (0, 255, 0)
            printTraker("Updated", i, mvTracker)
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
                ptx, pty = map(int, blob.pt)
                printMV(f"Dismissed:: Blob at {ptx, pty}.")
                continue # Do not create a tracker = continue to next iteration
            # Get and draw bbox:
            bbox = util.bboxFromKeypoint(blob, width_on_height_ratio = 0.5)
            blue = (255, 0, 0)

            # Create and register tracker:
            mvTracker = util.Namespace()
            mvTracker.tracker = self.mvTrackerCreator()
            mvTracker.tracker.init(frame, bbox)
            mvTracker.ret = True
            mvTracker.bbox = bbox
            mvTracker.pt = blob.pt
            blue = (255, 0, 0)
            printTraker("Created", len(trackerList), mvTracker)
            showTracker(im["frame"], mvTracker, blue)
            trackerList.append(mvTracker)


def showTracker(frame, mvTracker, color):
    cv2.rectangle(frame, *util.pointsFromBbox(mvTracker.bbox), color, thickness = 6)

def printTraker(msg, i, mvTracker):
    printMV(f"{msg}:: Tracker {i}: ret {mvTracker.ret}, bbox {mvTracker.bbox} --")