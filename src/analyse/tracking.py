import util

import cv2

import logging


class MvTracker(util.MvBbox):
    __slots__ = "tracker ret errCount history".split()

    smallestAllowedTrackerArea = 1_000

    def __init__(self, frameIndex, bbox, tracker, frame):
        super(MvTracker, self).__init__(*bbox)
        self.tracker = tracker
        self.tracker.init(frame, bbox)
        self.errCount = 0
        self.ret = True
        self.history = {frameIndex: bbox}
    
    def extract(self, frame, objLocation, horizon):
        """
        Extract the object from the frame and scale it for it to always have the same size.

        Extract an area of relevant size from `frame` at `objLocation` according
        to the distance to `horizon`. Scale it so that it makes a constant size,
        no matter the distance between the camera and the object.
        
        :param frame: Image (pixel matrix) from which to extract.
        :param objLocation: [x, y] - location of the object.
        :param horizon: x - position of the horizon.
        :return: A pixel matrix extracted and scaled from the image.
        """
        objX, objY = objLocation
        frameH, _frameW = frame.shape[:2]
        obj2h = objX - horizon
        bot2h = frameH - horizon
        targetWidth = 400
        targetHeight = 500
        if obj2h < 100:
            w = 24
        else:
            w = targetWidth * obj2h / bot2h
        h = int(targetHeight * w / targetWidth)
        w = int(w)

        x = objX - w // 2
        xx = x + w
        y = objY - h // 2
        yy = y + h
        if x < 0:

        # logging.getLogger("[MV]").debug(f"x: {x}, y: {y}, w: {w}, h: {h} -- objX: {objX}, objY: {objY}, fshape[:2]: {frame.shape[:2]}")
        exctracted = frame[x:x + w, y:y + h]
        scaled = cv2.resize(exctracted, (targetWidth, targetHeight), interpolation = cv2.INTER_CUBIC)
        cv2.imshow('Scaled', scaled)
        return scaled

    def updateTracker(self, frameIndex, frame):
        self.ret, bbox = self.tracker.update(frame)
        mvbbox = util.MvBbox(*bbox)
        if m
        self.extract(frame, , 0)
        if self.ret:
            self.errCount = 0
            self.updateBbox(frameIndex, bbox)
        else:
            self.errCount += 1

    def updateBbox(self, frameIndex, newBbox):
        self.history[frameIndex] = newBbox
        self.bbox = newBbox

    def isFinishedTracker(self, vidDimension):
        """Tell whether the given tracker should still be updated or is too small / out of screen and thus should be "Finished"."""
        finished = False
        height, _width = vidDimension
        if self.bottom > height * (1 - 0.08):
            finished = True
        if self.area < self.smallestAllowedTrackerArea:
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
    def __init__(self, logger, vidDimension, analyseData):
        self.logger = logger
        self.vidDimension = vidDimension
        self.trackerList = []
        self.analyseData = analyseData

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

    def mvTracking(self, im, frameIndex, frame, blobKeypoints):
        # A - Update trackers
        for mvTracker in self.trackerList:
            mvTracker.updateTracker(frameIndex, frame)
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
            green = (0, 255, 0)
            mvTracker.draw(im["frame"], green, thickness = 6)

        # F - Create trackers
        # bbox :: Bounding Box
        # Add new trakers for blobs whose keypoint location isn't inside a tracker bbox.
        _numberOfAdditions = 0
        for keypoint in blobKeypoints:
            if any(util.pointInBbox(keypoint.pt, mvTracker.bbox) for mvTracker in self.trackerList):
                # ptx, pty = map(int, blob.pt)
                # logger.debug(f"Dismissed:: Blob at {ptx, pty}.")
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
            mvTracker.draw(im["frame"], blue, thickness = 6)
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
                    # Given the current __contains__ definition in MvBbox (strict inclusion) 
                    # (as of 2018-06-06)
                    # This case should occure only when the two trackers perfecly overlap.
                    # This means that the below test is currently futile.
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
