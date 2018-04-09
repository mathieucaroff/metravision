import cv2
import numpy as np

def preTraitementVideo (video):
    """
    @description Soustrait le background, reconnait les blobs et réalise le tracking
    @param video cv.VideoCapture: La vidéo à traiter. Doit avoir été ouvert.
    @return shotlistlist [[Image]]: Pour chaque objet traqué, la liste des images ou il apparaît.
    """
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

    # coordTracklist = [] # Liste des coordonnées des trackers
    # trackCount = 0 # Nombre de trackers
    # trackSpeed = 5 # Vitesse du traquer (en pixels/image)
    # trackSpeedlist = [] # Liste des vitesses des trackers

    # motoCount6minutes = 0
    # motoCountVideoTotal = 0

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
        mask = fgMaskMOG2.astype(np.byte)
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

        coordPredicted = np.zeros(keypoints.shape, 2) # List des coordonnés des centres des blobs.
        predictionCount = 0

        for k in range(len(keypoints)):
            pt = keypoints.data[k].pt
            x = pt.x
            y = pt.y
            if y + L / 2 < height and y - L / 2 >= 0 and x + l / 2 < width and x - l / 2 >= 0:
                sub = bwImgCpy[y - L / 2 : y + L / 2][x - L / 2 : x + L / 2] # Extrait une copie de l'échantillon de l'image