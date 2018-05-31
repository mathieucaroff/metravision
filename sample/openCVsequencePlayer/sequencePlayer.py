import cv2
from pathlib import Path

videoPath = Path(r"C:\pi\Sequences6min\08a.avi").absolute()

assert videoPath.is_file(), f"The given path isn't a regular file :: {str(videoPath)}"

cap = cv2.VideoCapture(str(videoPath))



segmentDuration = 6 # seconds
fps = cap.get(cv2.CAP_PROP_FPS)
framePerSegment = int(fps * segmentDuration)

playBackSpeed = 1 # multiplicator
char = ""

while(True):
    for _ in range(playBackSpeed):
        ret, frame = cap.read()
    cv2.imshow('frame', frame)
    frameIndex = cap.get(cv2.CAP_PROP_POS_FRAMES)
    if frameIndex % framePerSegment == 0:
        char = chr(cv2.waitKey(0) & 0xFF)
    if char == 'q' or not ret:
        break
    if char == 'b':
        cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex - framePerSegment)
    if char == 's':
        playBackSpeed = 1
    if char == 'f':
        playBackSpeed = 2
    char = chr(cv2.waitKey(1) & 0xFF)