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

        alpha = 0.2
        topLeftCorner = alpha * bottomLeftCorner + (1 - alpha) * vanishingPoint
        topRightCorner = alpha * bottomRightCorner + (1 - alpha) * vanishingPoint
        del alpha
        
        #leftSide = 0.5 * bottomLeftCorner + 0.5 * topLeftCorner
        #rightSide = 0.5 * bottomRightCorner + 0.5 * topRightCorner

        
        height = topLeftCorner[1]
        assert abs(height - topLeftCorner[1]) < 1.0

        #Calculate the destination's points
        dstBottomLeftCorner = bottomLeftCorner
        dstBottomRightCorner = bottomRightCorner

        dstTopLeftCorner = np.array([self.xLeftEdge, height])
        dstTopRightCorner = np.array([self.xRightEdge, height])

        #dstLeftSide = 0.5 * dstBottomLeftCorner + 0.5 * dstTopLeftCorner
        #dstRightSide = 0.5 * dstBottomRightCorner + 0.5 * dstTopRightCorner

        sides = []
        dstSides = []
        for i in range(1, 8):
            alpha = i / 8
            sides.append( alpha * bottomLeftCorner + (1 - alpha) * topLeftCorner )
            sides.append( alpha * bottomRightCorner + (1 - alpha) * topRightCorner )
            dstSides.append( alpha * dstBottomLeftCorner + (1 - alpha) * dstTopLeftCorner )
            dstSides.append( alpha * dstBottomRightCorner + (1 - alpha) * dstTopRightCorner )
        
        #Analysis zone
        #tlp = (320,int(0.55*h))
        #trp = (610,int(0.55*h))
        #blp = (150, 500)
        #brp = (710, 500)
        #cv2.circle(img = frame, center = blp, radius = 15, color = (255,0,0), thickness = -1)
        #cv2.circle(img = frame, center = brp, radius = 15, color = (255,0,0), thickness = -1)
        #cv2.circle(img = frame, center = tlp, radius = 5, color = (255,0,0), thickness = -1)
        #cv2.circle(img = frame, center = trp, radius = 5, color = (255,0,0), thickness = -1)

        pts_src = np.array([topLeftCorner, topRightCorner, bottomLeftCorner, bottomRightCorner, *sides ]) # leftSide, rightSide]) #this didn't work very well
        pts_dst = np.array([dstTopLeftCorner, dstTopRightCorner, dstBottomLeftCorner, dstBottomRightCorner, *dstSides]) # dstLeftSide, dstRightSide])
        #pts_src = np.array([tlp, trp, blp, brp])
        #pts_dst = np.array([[0, 0], [700, 0], [0, h-1], [780, h-1]])
        dstW = self.xRightEdge - self.xLeftEdge
        dsize = dstW, 4 * h
        homographyMatrix, _status = cv2.findHomography(pts_src, pts_dst)
        #affine = cv2.getAffineTransform(pts_src, pts_dst) #error: (-215) src.checkVector(2, 5) == 3 && dst.checkVector(2, 5) == 3 in function cv::getAffineTransform
        #getPers = cv2.getPerspectiveTransform(pts_src, pts_dst) #same results of homofraphy

        warped = cv2.warpPerspective(frame, homographyMatrix, dsize)
        return warped


class DummyPerspectiveCorrector:
    def correct(self, frame):
        return frame