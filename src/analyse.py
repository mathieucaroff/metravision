import cv2
import numpy as np

import util
from util import printMV

class AnalyseTool():
    # Setup:
    def __init__(self, vidDimension, debug):
        """
        Parametre et crée le backgroundSubtractor () ainsi que le blob detector.
        """
        self.debug = debug

        # Background subtractor initialisation
        self.bgSub = cv2.createBackgroundSubtractorMOG2()

        # blobDetector initialisation
        params = cv2.SimpleBlobDetector_Params()
        params.minDistBetweenBlobs = 4
        params.filterByArea = True
        params.minArea = 2_000
        params.maxArea = 100_000
        params.filterByInertia = True
        params.maxInertiaRatio = 2
        self.blobDetector = cv2.SimpleBlobDetector_create(params)

        self.last_fgMask = self.oneBeforeLast_fgMask = np.zeros(shape = vidDimension, dtype = np.uint8) # Temporary value

        self.trackerList = []

    @staticmethod
    def mvTrackerCreator():
        """
        Crée et renvoie un tracker du type spécifié par la variable tracker_type.
        """
        tracker_type = 'KCF'

        tracker_create = {
            "BOOSTING": cv2.TrackerBoosting_create,
            "MIL": cv2.TrackerMIL_create,
            "KCF": cv2.TrackerKCF_create,
            "TLD": cv2.TrackerTLD_create,
            "MEDIANFLOW": cv2.TrackerMedianFlow_create,
            "GOTURN": cv2.TrackerGOTURN_create,
            # "CSRT": cv2.TrackerCSRT_create,
            # "MOSSE": cv2.TrackerMOSSE_create,
        }[tracker_type]

        tracker = tracker_create()

        return tracker


    # Run:
    def run(self, im):
        """
        Run the analyse of a frame.
        """
        sub = self.bgSub.apply(image = im["frame"]) #, learningRate = 0.05)
        im["fgMask"] = sub
        
        # Two-frame bitwise AND

        im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], self.last_fgMask, self.oneBeforeLast_fgMask)

        # erodeAndDilate
        mask = self.erodeAndDilate(im)
        _ = mask

        # Contour
        # self.contour(im, mask)

        # Blob Detector
        blobKeypoints = self.blobDetection(im, using = "dilateC")

        # Tracking
        frame = im["blob_dilateC"]
        self.mvTracking(im, frame, blobKeypoints)

        self.last_fgMask, self.oneBeforeLast_fgMask = im["fgMask"], self.last_fgMask

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
        Detecte les contours dans l'image et les dessine.
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


    def blobDetection(self, im, using):
        red = (0, 0, 255)
        ret = None
        imageNameList = list(im.keys()) # Buffered
        for imageName in imageNameList:
            if not "dilate" in imageName:
                continue
            image = 255 - 255 * (1 & im[imageName])
            blobKeypoints = self.blobDetector.detect(image)
            im[f"blob_{imageName}"] = cv2.drawKeypoints(
                image = image,
                keypoints = blobKeypoints,
                outImage = np.array([]),
                color = red,
                flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
            )
            if imageName == using:
                ret = blobKeypoints
        assert ret is not None, "The parameter `using` must be the name of a processed image."
        return ret


    def mvTracking(self, im, frame, blobKeypoints):
        # Update trakers
        oldTrackerList = self.trackerList
        self.trackerList = []
        for i, mvTracker in enumerate(oldTrackerList):
            mvTracker.ret, mvTracker.bbox = mvTracker.tracker.update(frame) # Error ?
            green = (0, 255, 0)
            printTracker("Updated", i, mvTracker)
            showTracker(im["frame"], mvTracker, green)
            if not mvTracker.ret or not any(mvTracker in otherMvTracker for otherMvTracker in self.trackerList):
                for j, otherMvTracker in reversed(list(enumerate(self.trackerList))):
                    if otherMvTracker in mvTracker:
                        self.trackerList.pop(j)
                        printTracker("Removed", j, otherMvTracker)
                self.trackerList.append(mvTracker)
            else:
                printTracker("Removed", i, mvTracker)


        util.glob(trackerList = self.trackerList)

        # bbox: Bounding Box
        # Add new trakers for blobs whose keypoint location isn't inside a tracker bbox.
        for blob in blobKeypoints:
            if any(util.pointInBbox(blob.pt, mvTracker.bbox) for mvTracker in self.trackerList):
                # ptx, pty = map(int, blob.pt)
                # printMV(f"Dismissed:: Blob at {ptx, pty}.")
                continue # Do not create a tracker = continue to next iteration
            # Get and draw bbox:
            bbox = util.bboxFromCircle(blob, width_on_height_ratio = 0.5)
            blue = (255, 0, 0)

            # Create and register tracker:
            mvTracker = util.MvTracker(*bbox)
            mvTracker.tracker = self.mvTrackerCreator()
            mvTracker.tracker.init(frame, bbox)
            mvTracker.ret = True
            mvTracker.size = blob.size
            blue = (255, 0, 0)
            printTracker("Created", len(self.trackerList), mvTracker)
            showTracker(im["frame"], mvTracker, blue)
            self.trackerList.append(mvTracker)


def showTracker(frame, mvTracker, color):
    cv2.rectangle(frame, *util.pointsFromBbox(mvTracker.bbox), color, thickness = 6)

def printTracker(msg, i, mvTracker):
    printMV(f"{msg}:: Tracker {i}: ret {mvTracker.ret}, bbox {[int(v) for v in mvTracker.bbox]} --")
