import cv2
import numpy as np

def pausevid (chemin):
    cap = cv2.VideoCapture(chemin)
    play = True
    while True:

        if play == True:
            ret, img = cap.read()
            if not ret:
                print ("error !!!!!")
        cv2.namedWindow('display', cv2.WINDOW_NORMAL)
        cv2.imshow('display', img)
        espace = 0x20
        if cv2.waitKey(2) & 0xFF == espace:
            play = not play
        
        elif cv2.waitKey(2) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
pausevid(r"C:\Users\eleve\Desktop\Cerema\short\soleil.avi")