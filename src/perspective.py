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

        #roadWidth = self.xRightEdge - self.xLeftEdge
        # margin = 0.1 * roadWidth
        bottomLeftCorner  = np.array([self.xLeftEdge, h - 1])
        bottomRightCorner = np.array([self.xRightEdge, h - 1])

        topLeftCorner = 0.4 * bottomLeftCorner + 0.6 * vanishingPoint
        topRightCorner = 0.4 * bottomRightCorner + 0.6 * vanishingPoint
        
        leftSide = 0.5 * bottomLeftCorner + 0.5 * topLeftCorner
        rightSide = 0.5 * bottomRightCorner + 0.5 * topRightCorner

        
        height = topLeftCorner[1]
        assert abs(height - topLeftCorner[1]) < 1.0

        #Calculate the destination's points
        dstBottomLeftCorner = bottomLeftCorner
        dstBottomRightCorner = bottomRightCorner

        dstTopLeftCorner = np.array([self.xLeftEdge, height])
        dstTopRightCorner = np.array([self.xRightEdge, height])

        dstLeftSide = 0.5 * dstBottomLeftCorner + 0.5 * dstTopLeftCorner
        dstRightSide = 0.5 * dstBottomRightCorner + 0.5 * dstTopRightCorner
        #Analisis zone
        tlp = (339,int(0.45*h))
        trp = (589,int(0.45*h))
        blp = (130, 600)
        brp = (720, 600)
        dblp = (0, 0)
        dbrp = (720, 0)
        dtlp = (100, h-1)
        dtrp = (720, h-1)
        cv2.circle(img = frame, center = blp, radius = 5, color = (255,0,0), thickness = -1)
        cv2.circle(img = frame, center = brp, radius = 5, color = (255,0,0), thickness = -1)
        cv2.circle(img = frame, center = tlp, radius = 5, color = (255,0,0), thickness = -1)
        cv2.circle(img = frame, center = trp, radius = 5, color = (255,0,0), thickness = -1)
        cv2.circle(img = frame, center = dblp, radius = 5, color = (0,0,255), thickness = -1)
        cv2.circle(img = frame, center = dbrp, radius = 5, color = (0,255,0), thickness = -1)
        cv2.circle(img = frame, center = dtlp, radius = 5, color = (0,0,255), thickness = -1)
        cv2.circle(img = frame, center = dtrp, radius = 5, color = (0,255,0), thickness = -1)
        #pts_src = np.array([topLeftCorner, topRightCorner, bottomLeftCorner, bottomRightCorner, leftSide, rightSide]) #this didn't work very well
        #pts_dst = np.array([dstTopLeftCorner, dstTopRightCorner, dstBottomLeftCorner, dstBottomRightCorner, dstLeftSide, dstRightSide])
        pts_src = np.array([tlp, trp, blp, brp], dtype = "float32")
        pts_dst = np.array([dblp, dbrp, dtlp, dtrp], dtype = "float32")
        pts_src = np.float32(pts_src)
        pts_dst = np.float32(pts_dst)
        dsize = w, h
        homographyMatrix, _status = cv2.findHomography(pts_src, pts_dst)
        #affine = cv2.getAffineTransform(pts_src, pts_dst) #error: (-215) src.checkVector(2, 5) == 3 && dst.checkVector(2, 5) == 3 in function cv::getAffineTransform
        #getPers = cv2.getPerspectiveTransform(pts_src, pts_dst) #same results of homofraphy

        warped = cv2.warpPerspective(frame, homographyMatrix, dsize)
        return warped


class DummyPerspectiveCorrector:
    def correct(self, frame):
        return frame