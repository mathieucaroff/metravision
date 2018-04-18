import cv2
import numpy as np
from util import Point, average


l = 60
L = 120

def preTraitementVideo (video):
    """
    @description Soustrait le background, reconnait les blobs et réalise le tracking
    @param video cv2.VideoCapture: La vidéo à traiter. Doit avoir été ouvert.
    @return shotlistlist [[Image]]: Pour chaque objet traqué, la liste des images ou il apparaît.
    """

    img = NotImplemented # Img
    imgpred = NotImplemented # Imgpred

    fps = video.get(cv2.CAP_PROP_FPS)
    frameIndex = 0
    # oldtime = 0
    # time = 0
    # resultData = [["Temps", "Nombre de Motos"]] # Données à écrire dans fichier résultats
    ok, frame = video.read()
    if not ok:
        raise RuntimeError("[MV] OpenCV cannot read from given video file")
    pMOG2 = cv2.BackgroundSubtractorMOG2()
    pMOG2.apply(frame)
    frameIndex = 1

    # Les 30 premières images sont utilisées pour déterminer le fond fixe.
    for i in range(1,30):
        if not video.read(frame):
            frameIndex = i - 1
            break
        pMOG2.apply(frame)
    
    height = frame.shape[0]
    width = frame.shape[1]
    channelCount = frame.shape[2]
    print(fps, frameIndex, width, height, channelCount)

    coordTracklist = [] # Liste des coordonnées des trackers
    trackCount = 0 # Nombre de trackers
    initialTrackSpeed = 5 # Vitesse du traquer (en pixels/image)
    trackSpeedlist = [initialTrackSpeed] * 5 # Liste des vitesses des trackers

    motoCount6minutes = 0
    motoCountVideoTotal = 0

    # création de 5 fenetres
    # cv2.namedWindow('win1')
    # cv2.setWindowTitle('win1', 'N&B')    

    # cv2.namedWindow('win2')
    # cv2.setWindowTitle('win2', 'BcgSub')

    # cv2.namedWindow('win3')
    # cv2.setWindowTitle('win3', 'Mask')

    # cv2.namedWindow('win4')
    # cv2.setWindowTitle('win4', 'Blob')

    # cv2.namedWindow('win5')
    # cv2.setWindowTitle('win5', 'Detection')
    while True:
        going, _ = video.read(frame)
        if not going:    # fin de la vidéo
            print("Fin de la video")
            # key = cv2.waitKey(0)
            break

        bwImg = cv2.cvtColor(frame, None, cv2.COLOR_BGR2GRAY)
        bwImgCpy = bwImg.clone()

        ### Background substraction
        fgMaskMOG2 = pMOG2.apply(frame)
        #mask = np.empty([height, width], dtype=np.byte).copy(fgMaskMOG2)
        mask = fgMaskMOG2.astype(np.bytes)
        cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY, mask)

        ### Erosion & Dilatation
        kernelErosion = cv2.getStructuringElement( cv2.MORPH_RECT, (4, 4) )
        kernelDilatation = cv2.getStructuringElement( cv2.MORPH_RECT, (5, 5) )
        cv2.erode(mask, kernelErosion, mask)
        cv2.dilate(mask, kernelDilatation, mask)

        mask = 255 - mask
        
        ### Blob detector
        params = cv2.SimpleBlobDetector_Params()

        # Changement des seuils
        params.minThreshold = 0
        params.maxThreshold = 255
        # Filtrage par zone
        params.filterByArea = True
        params.minArea = 500
        params.maxArea = 100000000
        # Filter by Circularity
        params.filterByCircularity = False
        # Filter by Convexity
        params.filterByConvexity = False
        # Filter by Inertia
        params.filterByInertia = False

        detector = cv2.SimpleBlobDetector(params) # détecte blobs
        keypoints = detector.detect(mask) # liste des coordonnées
        
        imgBlob = cv2.drawKeypoints(mask, keypoints) # mask + keypoints

        coordPredicted = [] # List des coordonnés des centres des blobs.

        for k in range(len(keypoints)):
            pt = keypoints.data[k].pt
            x = pt.x
            y = pt.y
            if y + L / 2 < height and y - L / 2 >= 0 and x + l / 2 < width and x - l / 2 >= 0:
                sub = bwImgCpy[y - L / 2 : y + L / 2][x - L / 2 : x + L / 2] # Extrait une copie de l'échantillon de l'image
                predicted = [True] # TODO [lua]`predicted = net:forward(sub:view(1, L, l))`
                if predicted[0] == True:
                    # NPredicted += 1
                    coordPredicted.append(Point(x, y))
                    for i in range(10, 27, 8):
                        cv2.circle(frame, 1, 8, 0, center = [x, y - 10], radius = i, color = [0, 0, 255])
                cv2.rectangle(img, pt1 = [x - l/2, y - L/2], pt2 = [x + l/2 - 1, y + L/2 - 1], color = [255] * 3)
        
        coordChanged = [False] * len(coordTracklist)

        for i in range(1, len(coordPredicted)):
            isNewMoto = True 
            for j in range(len(coordPredicted)):
                condX = abs(coordTracklist[j][0] - coordPredicted[i][0]) < 50 # si la distance entre l'ordonnée de l'ancienne prediction (traker) et le blob actuel < 50
                condY = abs(coordTracklist[j][1] - coordPredicted[i][1]) < 30 # si la distance entre l'abscisse de l'ancienne prediction et le blob actuel < 30
                if condX and condY:
                    isNewMoto = False
                    if abs(coordTracklist[j].y - coordPredicted[i].y) < 15: # si la vitesse (pixels/image) est <15
                        trackSpeedlist[:1] = [] # on supprime la vitesse la plus ancienne du tableau
                        currentSpeedY = abs(coordTracklist[j].y - coordPredicted[i].y) # on y ajoute la vitesse actuelle
                        trackSpeedlist.append(currentSpeedY)
                        trackSpeed = average(trackSpeedlist)
                    coordTracklist[j].x = coordPredicted[i].x
                    coordTracklist[j].y = coordPredicted[i].y
                    coordTracklist[j].z += 1
                    coordChanged[j] = True
                    # [LUA]
                    # if CoordTrack[j][3] > 5 then # cercle bleu indique que la moto sera comptée
                    # cv.circle{frame, center = {CoordTrack[j][1], CoordTrack[j][2]-10}, radius = 5, color = {255, 0, 0}, 1, 4, 0}
                    # end
            if isNewMoto:
                # Dessine un cercle vert sur la moto prédite
                green = [0, 255, 0]
                cv2.circle(1, 8, 0, frame, center = (coordPredicted[i].x, coordPredicted[i].y - 10), radius = 26, color = green)
                coordTracklist.append(Point(coordPredicted[i].x, coordPredicted[i].y, 0))
        
        for i in range(i, len(coordTracklist)):
            raise NotImplementedError

        # Retirons les doublons:
        j = 0
        while 0 <= j < len(coordTracklist):
            k = 1
            while 0 <= k < len(coordTracklist) and j >= 0:
                if k != j:
                    if coordTracklist[j].y == coordTracklist[k].y:
                        coordTracklist.pop(k)
                        j -= 1
                        k -= 1
                k += 1
            j += 1