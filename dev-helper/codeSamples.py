import cv2

videoLocationFormat = "/home/lox/video/%s"

def cvOpenVideoFileMp4():
    return cv2.VideoCapture(videoLocationFormat % "short/8s.mp4")

def cvOpenVideoFileAvi():
    return cv2.VideoCapture(videoLocationFormat % "short/test-9s.avi")

def cvTestLoadConfigFile():
    raise NotImplementedError