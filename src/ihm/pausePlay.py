"""
Permet la mise en pause et le retour à la lecture de la vidéo dans une fenêtre.
"""
import cv2

def pauseVid (cap):
    #cap = cv2.VideoCapture(nom)
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