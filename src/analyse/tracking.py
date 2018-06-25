import util

import cv2
import numpy as np

import logging


class DummyExtractor:
    def __init__(self, _0, _1, frame, *args, **kwargs):
        self.frame = frame

    def extract(self, *args, **kwargs):
        return self.frame
    
    def translateMvBboxInward(self, mvbbox):
        return mvbbox
    
    def translateMvBboxOutward(self, mvbbox):
        return mvbbox

class ActiveExtractor:
    """
    Used to extract and scale a region of an image, mapping MvBboxes back and
    forth between the extracted region and the image.
    """

    def __init__(self, objBottomY, centerLocation, frame, horizon = 0, regionWidth = 400, regionHeight = 500):
        """
        Extract the object from the frame and scale it for it to always have the same size.

        Extract an area of relevant size from `frame` at `objLocation` according
        to the distance to `horizon`. Scale it so that it makes a constant size,
        no matter the distance between the camera and the object.
        
        :param frame: Image (pixel matrix) from which to extract.
        :param objLocation: [x, y] - location of the center of the object.
        :param objBottomY: y position of the bottom of the object, used with horizon to determine extract box size.
        :param horizon: x - position of the horizon.
        :return: A pixel matrix extracted and scaled from the image.
        """
        self.horizon = horizon
        self.frame = frame
        self.frameH, self.frameW, self.frameChannels = frame.shape
        self.objBottomY = objBottomY
        self.targetWidth = regionWidth
        self.targetHeight = regionHeight
        obj2h = objBottomY - horizon
        bot2h = self.frameH - horizon
        self.ratio = obj2h / bot2h # Usually, ratio < 1
        if self.ratio < 0.06:
            raise ValueError("Object is too close to horizon: ratio = {}".format(self.ratio))
        self.originWidth = int(self.targetWidth * self.ratio)
        self.originHeight = int(self.targetHeight * self.ratio)
        self.centerLocation = centerLocation
        self.mvbbox = util.MvBbox(0, 0, self.originWidth, self.originHeight)
        self.mvbbox.center = self.centerLocation
    
    def extract(self, fillerColor = None):
        """
        Compute the region to extract, extract it to a buffer
        """
        extracted = self.mvbbox.extractFrom(self.frame)
        targetDim = (self.targetWidth, self.targetHeight)
        target = cv2.resize(extracted, targetDim, interpolation = cv2.INTER_CUBIC)
        assert len(target.shape) >= 2
        return target
    
    def translateMvBboxInward(self, mvbbox):
        """
        Map an mvbbox of the frame to an mvbbox of the extracted region.

        Given an mvBbox on the frame, gives the corresponding mvbbox on the
        extracted region. It can be out of the region.
        """
        # "Where is mvbbox compared to self.mvbbox?"
        x, y, width, height = mvbbox.bbox
        ratio = self.ratio
        inwX = (x - self.mvbbox.x) / ratio
        inwY = (y - self.mvbbox.y) / ratio
        inwW = width / ratio
        inwH = height / ratio
        return util.MvBbox(inwX, inwY, inwW, inwH)
    
    def translateMvBboxOutward(self, mvbbox):
        """
        Map an mvbbox of the extracted region to an mvbbox of the frame .
        
        Given an mvBbox on the extracted region, gives the corresponding mvbbox
        on the frame. It can be out of the frame.
        """
        # "Where is mvbbox compared to the frame?"
        x, y, width, height = mvbbox.bbox
        ratio = self.ratio
        outwX = x * ratio + self.mvbbox.x
        outwY = y * ratio + self.mvbbox.y
        outwW = width * ratio
        outwH = height * ratio
        return util.MvBbox(outwX, outwY, outwW, outwH)

class MvTracker():
    __slots__ = "logger tracker ok errCount history mvbbox im".split()

    smallestAllowedTrackerArea = 1_000

    def __init__(self, logger, frameIndex, frame, Extractor, extractorConfig, bbox, tracker, im):
        self.logger = logger
        self.errCount = 0
        self.ok = True
        self.history = {frameIndex: bbox}
        self.mvbbox = util.MvBbox(*bbox)
        self.im = im
        extractor = Extractor(
            self.mvbbox.bottom,
            self.mvbbox.center,
            frame, horizon = 0,
            regionWidth = extractorConfig["regionWidth"],
            regionHeight = extractorConfig["regionHeight"],
        )
        region = extractor.extract()
        assert len(region.shape) >= 2
        regMvbbox = extractor.translateMvBboxInward(self.mvbbox)
        self.tracker = tracker
        self.tracker.init(region, regMvbbox.bbox)

    def updateTracker(self, frameIndex, frame, Extractor, extractorConfig, im = None):
        try:
            extractor = Extractor(
                self.mvbbox.bottom,
                self.mvbbox.center,
                frame,
                horizon = 0,
                regionWidth = extractorConfig["regionWidth"],
                regionHeight = extractorConfig["regionHeight"]
            )
            region = extractor.extract()
            if im is not None:
                im["trackExtRegion"] = region
            self.ok, regBbox = self.tracker.update(region)
            regMvbbox = util.MvBbox(*regBbox)
            self.mvbbox = extractor.translateMvBboxOutward(regMvbbox)
        except ValueError as err:
            self.logger.info(err)
            self.ok = False
        if self.ok:
            self.errCount = 0
            self.updateBbox(frameIndex, self.mvbbox.bbox)
        else:
            self.errCount += 1

    def updateBbox(self, frameIndex, newBbox):
        self.history[frameIndex] = newBbox

    def isFinishedTracker(self, vidDimension):
        """Tell whether the given tracker should still be updated or is too small / out of screen and thus should be "Finished"."""
        finished = False
        height, _width = vidDimension
        if self.mvbbox.bottom > height * 0.99:
            finished = True
        if self.mvbbox.area < self.smallestAllowedTrackerArea:
            finished = True
        return finished

    def receive(self, logger, sender):
        """
        Replace the given tracker. Supposes that the "sender" tracker will be abandoned, and that we have to replace it.
        """
        info = "[{} frame(s) into {}]".format(len(sender.history), len(self.history))
        if max(sender.history.keys()) + 1 < min(self.history.keys()) or min(sender.history.keys()) - 1 > max(self.history.keys()):
            logger.debug(f"Not merging trackers with non-matching history. {info}")
        else:
            logger.debug(f"Trackers history merged. {info}")
            self.history.update(sender.history)


class MvMultiTracker():
    def __init__(self, logger, trackingConfig, vidDimension, analyseData):
        self.logger = logger
        self.trackingConfig = trackingConfig
        self.vidDimension = vidDimension
        self.trackerList = []
        self.analyseData = analyseData

        type_ = self.trackingConfig[0]["type"]
        if type_ not in "Boosting MIL KCF TLD MedianFlow GOTURN CSRT MOSSE".split():
            raise ValueError(f"MvConfiguration: inexistant tracker type `{type_}`")
        self.mvTrackerCreator = getattr(cv2, f"Tracker{type_}_create")

        self.distanceCorrectionConfig = {"regionWidth": 400, "regionHeight": 400}
        dcc = self.trackingConfig[0].get("distanceCorrection", None) # dcc is dist.correc.config
        if dcc is not None:
            self.Extractor = ActiveExtractor
            self.distanceCorrectionConfig.update(dcc)
        else:
            self.Extractor = DummyExtractor


    def mvTracking(self, im, frameIndex, frame, blobKeypoints):
        # A - Update trackers
        for mvTracker in self.trackerList:
            mvTracker.updateTracker(frameIndex, frame, self.Extractor, self.distanceCorrectionConfig, im)
        _numberOfUpdates = len(self.trackerList)

        # B - Remove tracker duplicates
        duplicates = self.getTrackerDuplicates()
        oldTrackerList = self.trackerList
        self.trackerList = []
        for i, mvTracker in enumerate(oldTrackerList):
            if i in duplicates:
                mvTrackerReplacement = oldTrackerList[duplicates[i]]
                mvTrackerReplacement.receive(self.logger, mvTracker)
            else:
                self.trackerList.append(mvTracker)
        _numberOfDeletions = len(duplicates)

        # C - Remove finished trackers (out of screen / too small trackers)
        _numberOfFinishs = 0
        oldTrackerList = self.trackerList
        self.trackerList = []
        for _i, mvTracker in enumerate(oldTrackerList):
            center = mvTracker.mvbbox.center
            blobMvBbox = getBlobMvBbox(im["dilateC"], center.x, center.y)
            if blobMvBbox.width > 0:
                ratio = blobMvBbox.height / blobMvBbox.width
                isMoto = ratio > 1.6
                kind = ["Car", "Moto"][isMoto]
                magenta = (255, 0, 255)
                cyan = (255, 255, 0)
                color = [magenta, cyan][isMoto]
                blobMvBbox.draw(im["trackers"], color)
            if mvTracker.isFinishedTracker(self.vidDimension):
                self.analyseData.addVehicle(mvTracker.history)
                white = (255, 255, 255)
                mvTracker.mvbbox.draw(im["trackers"], white)
                kind = self.analyseData.getData()[-1][1]
                self.logger.debug(f":: Finished vehicle [{kind}]")
                _numberOfFinishs += 1
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
            if mvTracker.ok:
                green = (0, 255, 0)
                mvTracker.mvbbox.draw(im["trackers"], green, thickness = 6)
            else:
                green = (0, 127, 0)
                mvTracker.mvbbox.draw(im["trackers"], green, thickness = 6)

        # F - Create trackers
        # bbox :: Bounding Box
        # Add new trackers for blobs whose keypoint location isn't inside a tracker bbox.
        _numberOfAdditions = 0
        for keypoint in blobKeypoints:
            if any(util.Point(*keypoint.pt) in mvTracker.mvbbox for mvTracker in self.trackerList):
                # ptx, pty = map(int, blob.pt)
                # logger.debug(f"Dismissed:: Blob at {ptx, pty}.")
                continue # Do not create a tracker = continue to next iteration
            # Get and draw bbox:
            x, y = keypoint.pt
            blobMvbbox = getBlobMvBbox(im["dilateC"], x, y)
            # width_on_height_ratio = blobMvbbox.width / blobMvbbox.height
            # width_on_height_ratio = 0.5

            # Create and register tracker:
            if blobMvbbox.area > 0:
                try:
                    mvTracker = MvTracker(
                        logger = self.logger,
                        frameIndex = frameIndex,
                        frame = frame,
                        Extractor = self.Extractor,
                        extractorConfig = self.distanceCorrectionConfig,
                        bbox = blobMvbbox.bbox,
                        tracker = self.mvTrackerCreator(),
                        im = im,
                    )
                except ValueError:
                    continue
            if mvTracker.isFinishedTracker(self.vidDimension):
                continue
            
            blue = (255, 0, 0)
            mvTracker.mvbbox.draw(im["trackers"], blue, thickness = 6)
            self.trackerList.append(mvTracker)
            _numberOfAdditions += 1

        # logger.debug(f"[Trackers] Updated {_numberOfUpdates} then Rmvd dups {_numberOfDeletions}, Rmvd fin {_numberOfFinishs}, Created {_numberOfAdditions}.")


    def getTrackerDuplicates(self):
        """
        For each pair of tracker, determines if one is contained in the other, add them as a .

        The exception is when both trackers contain each other, then the one with the smaller area is removed.
        In case they are the same area, the one appearing earlier in the list is removed.

        :rtype dict:
        :return: indexDict, mapping the index of each tracker which needs be removed, to the (larger) tracker whicr replaces it
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
                abInclusion = trackerA.mvbbox.center in trackerB.mvbbox
                baInclusion = trackerB.mvbbox.center in trackerA.mvbbox
                # v # x is the index to remove, if any. #
                if not abInclusion and not baInclusion:
                    # x = None
                    continue
                elif abInclusion:
                    x = a
                elif baInclusion:
                    x = b
                else:
                    # Given the current __contains__ definition in MvBbox (strict inclusion) 
                    # (as of 2018-06-06)
                    # This case should occure only when the two trackers perfecly overlap.
                    # This means that the below test is currently futile.
                    if trackerA.mvbbox.area <= trackerB.mvbbox.area:
                        x = a
                    else:
                        x = b
                y = a + b - x
                indexDict[x] = y
        assert iterCount == n * (n - 1) / 2
        return indexDict



def getBlobMvBbox(mask, xx, yy):
    """Explore the mask, left, right, up and down to determine the width and height of the blob at given point.
    
    :rtype MvBbox:
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
