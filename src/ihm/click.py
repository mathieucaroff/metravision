
import numpy as np
import cv2
import math


def on_mouse(event, x, y, flags, params):

    global boxes;
    global selection_in_progress;

    
    #currentMousePosition[0] = x;
    #currentMousePosition[1] = y;

    if event == cv2.EVENT_LBUTTONDOWN:
        boxes = [];
        print ('Start Mouse Position: '+str(x)+', '+str(y))
        sbox = [x, y];
        selection_in_progress = True;
        boxes.append(sbox);

    elif event == cv2.EVENT_LBUTTONUP:
        print ('End Mouse Position: '+str(x)+', '+str(y))
        ebox = [x, y];
        selection_in_progress = False;
        boxes.append(ebox);


video = r"C:\Users\eleves\Desktop\MV_IHM\bouchon-40s.mp4"
cap = cv2.VideoCapture(video)
bgSub = cv2.createBackgroundSubtractorMOG2()

cv2.setMouseCallback('cap', on_mouse)

while(cap.isOpened()):
    ret, frame = cap.read()
	
    frame = cv2.resize(frame, (0, 0), None, .5, .5)
    
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
    cv2.imshow('1',numpy_ver)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
       
cap.release()
cv2.destroyAllWindows()