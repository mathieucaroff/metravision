import cv2
import numpy as np
import util

class PerspectiveCorrector:
    def __init__(self, xLeftEdge, xRightEdge, vanishingPoint):
        self.xLeftEdge = xLeftEdge
        self.xRightEdge = xRightEdge
        self.vanishingPoint = vanishingPoint
    
    # https://www.learnopencv.com/homography-examples-using-opencv-python-c/
    def correct(self, frame):
        h, w, _colorNumber = frame.shape
        vanishingPoint = np.array(self.vanishingPoint)

        # roadWidth = self.xRightEdge - self.xLeftEdge
        # margin = 0.1 * roadWidth
        bottomLeftCorner  = np.array([self.xLeftEdge, h - 1])
        bottomRightCorner = np.array([self.xRightEdge, h - 1])

        topLeftCorner = 0.2 * bottomLeftCorner + 0.8 * vanishingPoint
        topRightCorner = 0.2 * bottomRightCorner + 0.8 * vanishingPoint

        height = topLeftCorner[1]
        assert abs(height - topRightCorner[1]) < 1.0

        pts_src = np.array([topLeftCorner, topRightCorner, bottomLeftCorner, bottomRightCorner])
        pts_dst = np.array([[self.xLeftEdge, height], [self.xRightEdge, height], bottomLeftCorner, bottomRightCorner])
        dsize = w, h

        homographyMatrix, _status = cv2.findHomography(pts_src, pts_dst)
        warped = cv2.warpPerspective(frame, homographyMatrix, dsize)
        return warped


class DummyPerspectiveCorrector:
    def correct(self, frame):
        return frame