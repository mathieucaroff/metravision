import cv2


def interval (chemin):
    
    cap = cv2.VideoCapture(chemin)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cv2.namedWindow('mywindow')
    cv2.createTrackbar( 'start', 'mywindow', 0, length, onChange )
    cv2.createTrackbar( 'end'  , 'mywindow', 100, length, onChange )

    onChange(0, cap)
    cv2.waitKey()

    start = cv2.getTrackbarPos('start','mywindow')
    end   = cv2.getTrackbarPos('end','mywindow')
    if start >= end:
        raise Exception("start must be less than end")

    cap.set(cv2.CAP_PROP_POS_FRAMES,start)
    while cap.isOpened():
        ret,img = cap.read()
        if not ret:
            print("error!!!!")
        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            break
        cv2.imshow("mywindow", img)
        k = cv2.waitKey(10) & 0xff
        if k==27:
            break
def onChange(trackbarValue, cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES,trackbarValue)
    #img = cap.read()
    #cv2.imshow("mywindow", img)
    #pass
interval(r"C:\Users\eleve\Desktop\Cerema\short\soleil.avi")