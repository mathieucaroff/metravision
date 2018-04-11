import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
import random

def main():
    videoPath = "C:\\pi\\SequencesCourtes\\8s.mp4"

    cap = cv2.VideoCapture(videoPath)

    fps = cap.get(cv2.CAP_PROP_FPS)

    timePerFrame = 3 / fps

    bgSub = cv2.createBackgroundSubtractorMOG2()

    start = time.clock()
    for frameIdx in range(1, 1_000_000_000):
        if loop(frameIdx, cap, timePerFrame, bgSub, start) == "break":
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def imshow():
    windowNameList = "frame fgMask dilateMaskA erodeMaskA dilateMaskB erodeMaskB".split()

def loop(frameIdx, cap, timePerFrame, bgSub, start):

    jumpTo(cap, (frameIdx % 25) / 25)

    # Capture frame-by-frame
    ret, frame = cap.read()


    fgMask = bgSub.apply(image = frame, learningRate = 0.1)

    # erodeAndDilate
    mask = fgMask

    erodeA = 4
    dilateA = 30
    erodeB = 35
    dilateB = erodeA + erodeB - dilateA

    mask = cv2.erode(mask, easyKernel(erodeA))
    erodeMaskA = mask

    mask = cv2.dilate(mask, easyKernel(dilateA))
    dilateMaskA = mask

    mask = cv2.erode(mask, easyKernel(erodeB))
    erodeMaskB = mask

    mask = cv2.dilate(mask, easyKernel(dilateB))
    dilateMaskB = mask

    edMask = mask

    # Display the resulting frame
    cv2.imshow('frame', frame)
    cv2.imshow('fgMask', fgMask)
    cv2.imshow('erodeMaskA', erodeMaskA)
    cv2.imshow('dilateMaskA', dilateMaskA)
    cv2.imshow('erodeMaskB', erodeMaskB)
    cv2.imshow('dilateMaskB', dilateMaskB)

    controlledTime = (start + timePerFrame * frameIdx) - time.clock()
    if cv2.waitKey(max(0, int(1000 * controlledTime)) + 1) & 0xFF == ord('q'):
        return "break"
    if any(map(windowClosed, windowNameList)):
        return "break"
    return "continue"

def windowClosed(windowName):
    """Checking for a property of the window to tell whether it is (still) open."""
    whatever = cv2.WND_PROP_FULLSCREEN
    return cv2.getWindowProperty(windowName, whatever) == -1

def easyKernel(size, sizeX = None):
    """Generate an OpenCV kernel objet of given size.
    Note: I haven't checked the sizeX parameter"""
    sizeY = size
    if sizeX is None:
        sizeX = size
    return cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (sizeY, sizeX) )

def jumpTo(cap, fraction):
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frameIndex = int(fraction * frameCount)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)

if __name__ == "__main__":
    main()