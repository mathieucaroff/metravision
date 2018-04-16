
import numpy as np
import cv2
import sys
import math


video = r"C:\Users\eleves\Desktop\MV_IHM\bouchon-40s.mp4"
cap = cv2.VideoCapture(video)
bgSub = cv2.createBackgroundSubtractorMOG2()




while(cap.isOpened()):
    
    ret, frame = cap.read()
    
    
    fgMask = bgSub.apply(image = frame, learningRate = 0.1)

    
	
    # erodeAndDilate
    mask = fgMask

    erodeA = 4
    dilateA = 30
    erodeB = 35
    dilateB = erodeA + erodeB - dilateA

    mask = cv2.erode(mask, cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (erodeA, erodeA) ))
    erodeMaskA = mask

    mask = cv2.dilate(mask, cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (dilateA, dilateA) ))
    dilateMaskA = mask

    mask = cv2.erode(mask, cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (erodeB, erodeB) ))
    erodeMaskB = mask

    mask = cv2.dilate(mask, cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (dilateB, dilateB) ))
    dilateMaskB = mask

    edMask = mask
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
    numpy_horizontal = np.hstack((gray, fgMask, erodeMaskA))
    numpy_horizontal2 = np.hstack((dilateMaskA, erodeMaskB, dilateMaskB))
    
    numpy_ver = np.concatenate((numpy_horizontal, numpy_horizontal2), axis=0)
    
    cv2.namedWindow('1')

    """    
    #cv2.setMouseCallback('1', getPosition)
    
    #height and width define the limits of each video - imghpx and imgwpx
    ohpx, owpx = numpy_ver.shape[0:2] #pixel's number of output (same of imagList if it is not declare) It's necessary modifie to parameters defined by user
    imghpx = ohpx // 2
    imgwpx = owpx // 3
    
    if px < imgwpx and py < imghpx:
        cv2.namedWindow('Selected')
        cv2.imshow('Selected', gray)
    
    cv2.imshow('1',numpy_ver)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break """
       
cap.release()
cv2.destroyAllWindows()