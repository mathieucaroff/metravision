import cv2
import numpy as np
import math

import util
from util import first

from analyse.segmenting import AnalyseData, RealSegmenter

from analyse.tracking import MvMultiTracker

class ProcessingTool():
    # Setup:
    def __init__(
            self,
            logger,
            processingToolsConfig,
            vidDimension,
            timePerFrame,
            jumpEventSubscriber,
            segmentDuration = 60,
        ):
        """
        Initialisation -- Crée le backgroundSubtractor, paramètre le blob detector, initialise MultiTracker et AnalyseData.

        :param: logger:
        :param: vidDimension est la paire (width, height) pour le flux video traié
        :param: float timePerFrame: le temps de chaque trame (l'inverse de la quantité de trames par seconde)
        :param: jumpEventSubscriber:
        :param: int segmentDuration: la duration de chaque segment de vidéo est exprimé en secondes

        """
        
        self.logger = logger
        self.processingToolsConfig = processingToolsConfig
        self.vidDimension = vidDimension

        # Background subtractor initialisation
        backgroundSubstractorConfig = self.processingToolsConfig.backgroundSubstractor
        # for conf in backgroundSubstractor[1:]:
        # backgroundSubstractor
        type_ = backgroundSubstractorConfig[0]["type"]
        self.bgSub = {
            "KNN": cv2.createBackgroundSubtractorKNN,
            "MOG": None,
            "MOG2": cv2.createBackgroundSubtractorMOG2,
        }[type_]()

        # blobDetector initialisation
        blobDetectorConfig = processingToolsConfig.blobDetector
        bdp = blobDetectorConfig[0]["parameters"]
        sbParams = cv2.SimpleBlobDetector_Params()
        props = "filterByArea filterByCircularity filterByColor filterByConvexity filterByInertia maxArea maxCircularity maxConvexity maxInertiaRatio maxThreshold minArea minCircularity minConvexity minDistBetweenBlobs minInertiaRatio minRepeatability minThreshold thresholdStep".split()
        for paramName in bdp.keys():
            assert paramName in props, f"Parameter {paramName} isn't valid."
        for paramName, paramValue in bdp.items():
            setattr(sbParams, paramName, paramValue)
        self.blobDetector = cv2.SimpleBlobDetector_create(sbParams)

        self.last_fgMask = None
        self.oneBeforeLast_fgMask = None
        self.last_frame = None
        self.oneBeforeLast_frame = None
        # self.opticalFlow

        # Where to store results, together with the vehicle counter (segmenter)
        segmentDuration = 6 # seconds
        numberOfFramePerSegment = int(0.5 + segmentDuration / timePerFrame)
        segmenter = RealSegmenter(self.logger, numberOfFramePerSegment, timePerFrame)
        self.analyseData = AnalyseData(timePerFrame, jumpEventSubscriber, segmenter)

        # Multi Tracker initialisation
        self.mvMultiTracker = MvMultiTracker(
            self.logger,
            processingToolsConfig.tracking,
            vidDimension,
            self.analyseData,
        )
        self.trackerList = []

    def getData(self):
        # return self.analyseData.getData()
        return self.analyseData.segmenter.getData()

    # Run:
    def run(self, im, frameIndex):
        """
        Éxecuter l'analyse d'une trame.

        :param: np.array im: ensemble de trames
        :param: int frameIndex: index de chaque trame
        
        """
        sub = util.timed(self.bgSub.apply)(image = im["frame"], learningRate = 0.009)
        im["fgMask"] = sub
        
        # Two-frame bitwise AND
        
        if self.last_fgMask is None:
            self.last_fgMask = im["fgMask"]
        if self.oneBeforeLast_fgMask is None:
            self.oneBeforeLast_fgMask = self.last_fgMask
        
        im["bitwise_fgMask_and"] = cv2.bitwise_and(im["fgMask"], self.last_fgMask, self.oneBeforeLast_fgMask)

        # opticalFlow
        if self.processingToolsConfig.opticalFlow:
            im["opticalFlowH"], im["opticalFlowV"] = util.timed(self.opticalFlow)(im["frame"])
        
        # erodeAndDilate
        ptc = self.processingToolsConfig
        mask = util.timed(self.erodeAndDilate)(im,
            eadPre  = ptc.erodeAndDilatePreBitwiseAnd,
            eadPost = ptc.erodeAndDilatePostBitwiseAnd,
        )
        _ = mask

        # Contour
        if self.processingToolsConfig.contour:
            util.timed(self.contour)(im, mask)

        # Blob Detector
        blobKeypoints = util.timed(self.blobDetection)(im, nameOfImageToUse = "dilateC")

        # Tracking
        frame = im["blob_dilateC"]
        util.timed(self.mvMultiTracker.mvTracking)(im, frameIndex, frame, blobKeypoints)

        self.analyseData.tick()

        self.last_fgMask, self.oneBeforeLast_fgMask = im["fgMask"], self.last_fgMask
        self.last_frame, self.oneBeforeLast_frame = im["frame"], self.last_frame


    def opticalFlow(self, frame):
        """
        Compute the horizontal and vertical optical flow between successive frames.
        Calcul le flux optique horizontal et vertical entre des frames sucessives.

        :param: np.array frame:  trame actuel

        """
        if self.last_frame is None:
            self.last_frame = frame
        if self.oneBeforeLast_frame is None:
            self.oneBeforeLast_frame = self.last_frame
        
        opticalFlowH = np.array(self.last_frame)
        opticalFlowV = np.array(self.last_frame)
        for i in range(3):
            prev = self.last_frame[:, :, i]
            next_ = frame[:, :, i]
            
            OF = cv2.calcOpticalFlowFarneback(
                prev = prev,
                next = next_,
                flow = None,
                pyr_scale = 0.5,
                levels = 3,
                winsize = 20,
                iterations = 3,
                poly_n = 5,
                poly_sigma = 1.2,
                flags = 0)
            
            # boostedOF = np.vectorize(lambda x: math.sqrt(x) if x >= 0 else -math.sqrt(-x))(opticalFlow)
            boostedOF = OF
            absmax = np.max(np.abs(boostedOF))
            normedAround128 = 128 + (128 / absmax) * boostedOF
            intOpticalFlow = cv2.convertScaleAbs(normedAround128)

            opticalFlowH[:,:,i] = intOpticalFlow[:,:,0]
            opticalFlowV[:,:,i] = intOpticalFlow[:,:,1]
        return opticalFlowH, opticalFlowV

    @classmethod
    def erodeAndDilate(cls, im, eadPre, eadPost):
        """
        `ead` = erodeAndDilate
        Erode et Dilate l'image plusieurs fois.

        :param: np.array im: ensemble de trames
        :param: eadPre: paramètres de configuration de l'érosion et dilatation avant l'application du ET logique
        :param: eadPost: paramètres de configuration de l'érosion et dilatation après l'application du ET logique
        :return: le résultat de la trame après passer par les plusieurs processus d'érosion et dilatation, un ET logique et un processus de dilatation
        
        """
        mask = im["bitwise_fgMask_and"]

        for i, op in enumerate(eadPre):
            key, val = first(op.items())
            assert key in "erode dilate".split()
            erodeOrDilate = getattr(cv2, key)
            mask = erodeOrDilate(mask, cls.easyKernel(val))
            im[f"{key}Mask{'ABCDEFGHI'[i]}"] = mask
        
        mask = cv2.bitwise_and(mask, im["fgMask"])
        im["bitwise_fgMask_dilateB_and"] = mask

        # COPYPASTA COPYPASTA COPYPASTA
        for i, op in enumerate(eadPost):
            key, val = first(op.items())
            assert key in "erode dilate".split()
            erodeOrDilate = getattr(cv2, key)
            mask = erodeOrDilate(mask, cls.easyKernel(val))
            im[f"{key}{'CDEFGHI'[i]}"] = mask

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
    def contour(im, mask, ):
        """
        Detecte les contours dans l'image et les dessine.

        :param: np.array im: ensemble de trames
        :param: mask: résultat de la trame après le processus d'érosion et dilatation, et ET logique

        """
        red = (0, 0, 255)

        _img, contourPointList, _hierachy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        im["dilateMaskB"] = cv2.cvtColor(im["dilateMaskB"], cv2.COLOR_GRAY2BGR)

        allContours = -1
        cv2.drawContours(
            image = im["dilateMaskB"],
            contours = contourPointList,
            contourIdx = allContours,
            color = red
        )


    def blobDetection(self, im, nameOfImageToUse):
        """
        Détecte les blobs sur les images dont le nom contient "dilate".

        :param: np.array im: ensemble de trames
        :param: np.array nameOfImageToUse: il ontient lesquelles images ont été dilatées
        :return: les points clés des blobs
        
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