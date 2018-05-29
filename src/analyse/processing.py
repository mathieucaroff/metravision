import cv2
import numpy as np

import util
from util import printMV


from analyse.segmenting import AnalyseData

from analyse.tracking import MvTracker

class AnalyseTool():
    # Setup:
    def __init__(self, vidDimension, timePerFrame, jumpEventSubscriber):
        """
        Paramètre et crée le backgroundSubtractor () ainsi que le blob detector.
        """

        self.vidDimension = vidDimension

        # Background subtractor initialisation
        self.bgSub = cv2.createBackgroundSubtractorKNN()

        # blobDetector initialisation
        params = cv2.SimpleBlobDetector_Params()
        params.minDistBetweenBlobs = 4
        params.filterByArea = True
        params.minArea = 2_000
        params.maxArea = 20_000
        params.filterByInertia = True
        params.maxInertiaRatio = 3
        self.blobDetector = cv2.SimpleBlobDetector_create(params)

        self.last_fgMask = self.oneBeforeLast_fgMask = np.zeros(shape = vidDimension, dtype = np.uint8) # Temporary value

        # Tracker initialisation
        self.trackerList = []

        # Where to store results
        self.analyseData = AnalyseData(timePerFrame, jumpEventSubscriber)
    
    def getData(self):
        return self.analyseData.getData()

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
    def run(self, im, frameIndex):
        """
        Run the analysis of a frame.
        """
        sub = util.timed(self.bgSub.apply)(image = im["frame"], learningRate = 0.009)
        im["fgMask"] = sub
        
        # Two-frame bitwise AND

        im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], self.last_fgMask, self.oneBeforeLast_fgMask)

        # erodeAndDilate
        mask = util.timed(self.erodeAndDilate)(im)
        _ = mask

        # Contour
        # self.contour(im, mask)

        # Blob Detector
        blobKeypoints = util.timed(self.blobDetection)(im, nameOfImageToUse = "dilateC")

        # Tracking
        frame = im["blob_dilateC"]
        util.timed(self.mvTracking)(im, frameIndex, frame, blobKeypoints)

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
        dilateC = 15

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

        _img, contourPointList, _hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        im["dilateMaskA"] = cv2.cvtColor(im["dilateMaskA"], cv2.COLOR_GRAY2BGR)

        allContours = -1
        cv2.drawContours(
            image = im["dilateMaskA"],
            contours = contourPointList,
            contourIdx = allContours,
            color = red
        )


    def blobDetection(self, im, nameOfImageToUse):
        """
        Detecte les blobs sur les images dont le nom contient "dilate".
        """
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
            if imageName == nameOfImageToUse:
                ret = blobKeypoints
        assert ret is not None, "The parameter `nameOfImageToUse` must be the name of a processed image."
        return ret


    def mvTracking(self, im, frameIndex, frame, blobKeypoints):
        # A - Update trackers
        for mvTracker in self.trackerList:
            mvTracker.updateTracker(frameIndex, frame)
        numberOfUpdates = len(self.trackerList)

        # B - Remove tracker duplicates
        duplicates = self.getTrackerDuplicates()
        oldTrackerList = self.trackerList
        self.trackerList = []
        for i, mvTracker in enumerate(oldTrackerList):
            if i in duplicates:
                mvTrackerReplacement = oldTrackerList[duplicates[i]]
                mvTrackerReplacement.receive(mvTracker)
                # mvTracker.printTracker("Removed dup", i)
            else:
                self.trackerList.append(mvTracker)
        numberOfDeletions = len(duplicates)

        # C - Remove finished trackers (out of screen / too small trackers)
        numberOfFinishs = 0
        oldTrackerList = self.trackerList
        self.trackerList = []
        for mvTracker in oldTrackerList:
            center = mvTracker.center
            blobMvBbox = getBlobMvBbox(im["dilateC"], center.x, center.y)
            if blobMvBbox.width > 0:
                ratio = blobMvBbox.height / blobMvBbox.width
                isMoto = ratio > 1.6
                kind = ["Car", "Moto"][isMoto]
                magenta = (255, 0, 255)
                cyan = (255, 255, 0)
                color = [magenta, cyan][isMoto]
                blobMvBbox.draw(im["frame"], color)
            if mvTracker.isFinishedTracker(self.vidDimension):
                self.analyseData.addVehicle(mvTracker.history)
                white = (255, 255, 255)
                mvTracker.draw(im["frame"], white)
                kind = self.analyseData.getData()[-1][1]
                printMV(f":: Finished vehicle [{kind}]")
                numberOfFinishs += 1
                # mvTracker.printTracker("Removed fin", i)
            else:
                self.trackerList.append(mvTracker)

        # D - Remove lost trackers
        oldTrackerList = self.trackerList
        self.trackerList = []
        for mvTracker in oldTrackerList:
            if mvTracker.errCount < 10:
                self.trackerList.append(mvTracker)

        # Can help for debugging purpose
        util.glob(trackerList = self.trackerList)

        # E - Show existing trackers
        for mvTracker in self.trackerList:
            green = (0, 255, 0)
            # mvTracker.printTracker("Updated", i)
            mvTracker.draw(im["frame"], green, thickness = 6)

        # F - Create trackers
        # bbox :: Bounding Box
        # Add new trakers for blobs whose keypoint location isn't inside a tracker bbox.
        numberOfAdditions = 0
        for keypoint in blobKeypoints:
            if any(util.pointInBbox(keypoint.pt, mvTracker.bbox) for mvTracker in self.trackerList):
                # ptx, pty = map(int, blob.pt)
                # printMV(f"Dismissed:: Blob at {ptx, pty}.")
                continue # Do not create a tracker = continue to next iteration
            # Get and draw bbox:
            x, y = keypoint.pt
            blobMvbbox = getBlobMvBbox(im["dilateC"], x, y)
            # width_on_height_ratio = blobMvbbox.width / blobMvbbox.height
            # width_on_height_ratio = 0.5
            # bbox = util.bboxFromCircle(keypoint, width_on_height_ratio = width_on_height_ratio)

            # Create and register tracker:
            mvTracker = MvTracker(
                frameIndex = frameIndex,
                bbox = blobMvbbox.bbox,
                tracker = self.mvTrackerCreator(),
                frame = frame
            )
            if mvTracker.isFinishedTracker(self.vidDimension):
                continue
            
            blue = (255, 0, 0)
            # mvTracker.printTracker("Created", i = len(self.trackerList))
            mvTracker.draw(im["frame"], blue, thickness = 6)
            self.trackerList.append(mvTracker)
            numberOfAdditions += 1

        # printMV(f"[Trackers] Updated {numberOfUpdates} then Rmvd dups {numberOfDeletions}, Rmvd fin {numberOfFinishs}, Created {numberOfAdditions}.")


    def getTrackerDuplicates(self):
        """
        For each pair of tracker, if one is contained in the other, remove it.
        The exception is when both trackers contain each other, then the one with the smaller area is removed.
        In case they are the same area, the one appearing earlier in the list is removed.
        """
        indexDict = dict()
        iterCount = 0
        n = len(self.trackerList)
        for b, trackerA in enumerate(self.trackerList):
            for a, trackerB in enumerate(self.trackerList):
                if a >= b:
                    break
                # ^ # So we are sure we always have a < b #
                iterCount += 1
                abInclusion = trackerA in trackerB
                baInclusion = trackerB in trackerA
                # v # x is the index to remove, if any. #
                if not abInclusion and not baInclusion:
                    # x = None
                    continue
                elif abInclusion:
                    x = a
                elif baInclusion:
                    x = b
                else:
                    if trackerA.area <= trackerB.area:
                        x = a
                    else:
                        x = b
                y = a + b - x
                indexDict[x] = y
        assert iterCount == n * (n - 1) / 2
        return indexDict



def getBlobMvBbox(mask, xx, yy):
    """Explore the mask, left, right, up and down to determine the width and height of the blob at given point.
    
    Returns an MvBbox.
    """
    xx, yy = int(xx), int(yy)
    height, width = mask.shape
    assert xx < width
    assert yy < height
    left = 0
    for x in range(xx, -1, -1):
        if mask[yy, x] == 0:
            break
        left += 1
    right = 0
    for x in range(xx, width):
        if mask[yy, x] == 0:
            break
        right += 1

    up = 0
    for y in range(yy, -1, -1):
        if mask[y, xx] == 0:
            break
        up += 1
    down = 0
    for y in range(yy, height):
        if mask[y, xx] == 0:
            break
        down += 1

    xorigin = xx - left
    yorigin = yy - up
    width = left + right
    height = up + down

    return util.MvBbox(xorigin, yorigin, width, height)
