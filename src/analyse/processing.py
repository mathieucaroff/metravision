import cv2
import numpy as np

import util
from util import printMV


from analyse.segmenting import AnalyseData, RealSegmenter

from analyse.tracking import MvMultiTracker

class ProcessingTool():
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

        self.last_fgMask = None
        self.oneBeforeLast_fgMask = None

        # Where to store results, together with the vehicle counter (segmenter)
        segmentDuration = 10 # seconds
        numberOfFramePerSegment = int(0.5 + segmentDuration / timePerFrame)
        segmenter = RealSegmenter(numberOfFramePerSegment, timePerFrame)
        self.analyseData = AnalyseData(timePerFrame, jumpEventSubscriber, segmenter)

        # Multi Tracker initialisation
        self.mvMultiTracker = MvMultiTracker(vidDimension, self.analyseData)
        self.trackerList = []
    
    def getData(self):
        # return self.analyseData.getData()
        return self.analyseData.segmenter.getData()


    # Run:
    def run(self, im, frameIndex):
        """
        Run the analysis of a frame.
        """
        sub = util.timed(self.bgSub.apply)(image = im["frame"], learningRate = 0.009)
        im["fgMask"] = sub
        
        # Two-frame bitwise AND
        
        if self.last_fgMask is None:
            self.last_fgMask = im["fgMask"]
        if self.oneBeforeLast_fgMask is None:
            self.oneBeforeLast_fgMask = self.last_fgMask
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
        util.timed(self.mvMultiTracker.mvTracking)(im, frameIndex, frame, blobKeypoints)

        self.analyseData.tick()

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
            if imageName == nameOfImageToUse:
                image = 255 - 255 * (1 & im[imageName])
                blobKeypoints = self.blobDetector.detect(image)
                im[f"blob_{imageName}"] = cv2.drawKeypoints(
                    image = image,
                    keypoints = blobKeypoints,
                    outImage = np.array([]),
                    color = red,
                    flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
                )
                ret = blobKeypoints
        assert ret is not None, "The parameter `nameOfImageToUse` must be the name of a processed image."
        return ret