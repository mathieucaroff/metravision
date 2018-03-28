import cv2

def preTraitementVideo (video):
    """
    @description Soustrait le background, reconnait les blobs et réalise le tracking
    @param video cv.VideoCapture: La vidéo à traiter. Doit avoir été ouvert.
    @return shotlistlist [[Image]]: Pour chaque objet traqué, la liste des images ou il apparaît.
    """
    fps = video.get(cv2.CAP_PROP_FPS)
    frameIndex = 0
    time = 0
    time = 0
    resultData = [["Temps", "Nombre de Motos"]] # Données à écrire dans fichier résultats
    pMOG2 = cv2.BackgroundSubtractorMOG2()
    retCode, frame = video.read()
    width = frame.size()[0]
    height = frame.size()[1]
    pMOG2.apply(frame)

    # Les 30 premières images sont utilisées pour déterminer le fond fixe.
    for i in range(0,30):
        if not video.read(frame):
            frameIndex = i - 1
            break
        pMOG2.apply(frame)
    