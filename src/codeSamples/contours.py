import cv2
import numpy as np

cap = cv2.VideoCapture(r"C:\Users\eleve\Desktop\Cerema\soleil.avi")
while True:
    ret, img = cap.read()
    if not ret:
        print("error !!!!")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _,threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    _,contours,_ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    print("number of contours detected", len(contours))
    cv2.drawContours(img, contours, -1, (0,0,255), 1)
    cv2.namedWindow('display', cv2.WINDOW_NORMAL)
    cv2.imshow('display', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()