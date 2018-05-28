import util
from util import printMV


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