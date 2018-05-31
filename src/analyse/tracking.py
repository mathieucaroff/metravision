import util
from util import printMV

import cv2


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
    
    def updateTracker(self, frameIndex, frame):
        self.ret, bbox = self.tracker.update(frame) # Error ?
        if self.ret:
            self.errCount = 0
            self.updateBbox(frameIndex, bbox)
        else:
            self.errCount += 1
        # self.printTracker("Updated", i)
    
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

    def printTracker(self, msg, i):
        printMV(f"{msg}:: Tracker {i}: ret {self.ret}, bbox {self.bbox} --")
    
    def receive(self, sender):
        """
        Replace the given tracker. Supposes that the "sender" tracker will be abandoned, and that we have to replace it.
        """
        if max(sender.history.keys()) + 1 < min(self.history.keys()) or min(sender.history.keys()) - 1 > max(self.history.keys()):
            printMV("[Warning] trackers with non-matching history merged -- canceled.")
        else:
            self.history.update(sender.history)


class MvMultiTracker():
    def __init__(self, vidDimension, analyseData):
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
