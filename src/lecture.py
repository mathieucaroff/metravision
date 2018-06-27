import collections

import time

import cv2
import numpy as np

# import matplotlib.pyplot as plt

import util

import analyse.processing as processing

class PlaybackStatus:
    """
    Contient les informations liées à l'état de lecture d'une vidéo.
    
    Ceci permet aux différentes parties du logicielle de communiquer entre elles.
    :param play: Est vrai lorsque la video est en cours de lecture.
    :param endReached: Indique qu' il faut passer à la vidéo suivante car la fin
        de la vidéo à été atteinte ou car l'utilisateur l'a demandé.
    :param quitting: Indique qu'il faut quitter l'application, généralement car
        l'utilisateur l'a demandé.
    :param refreshNeeded: Indique qu'il faut lire une frame car l'affichage n'est
        plus à jour ou car l'utilisateur l'a demandé. Est utile lorsque la vidéo
        est en pause et que l'utilisateur à demander un saut.
    """
    __slots__ = "play endReached quitting refreshNeeded".split()
    def __init__(self, play=True, endReached=False, quitting=False, refreshNeeded=False):
        self.play = play
        self.endReached = endReached
        self.quitting = quitting
        self.refreshNeeded = refreshNeeded


class TimeController:
    """
    Ensures a regular time flow in the application. Prevents the time to flow faster than the recorded video time.

    ---

    Assure un écoulement régulier du temps entre chaque frame.

    Ne s'applique que lorsque le traitement de la vidéo est plus rapide que sa
    vitesse de lecture prévue. Ainsi, la vidéo n'est ralentie que lorsqu'elle
    aurait été lue trop vite.
    """
    def __init__(self, timePerFrame):
        self.timePerFrame = timePerFrame
        self.reset()

    def reset(self):
        self.referenceTime = time.clock()
        self.timeIndex = 0

    def getControlledTime(self):
        self.timeIndex += 1
        controlledTime = (self.referenceTime + self.timePerFrame * self.timeIndex) - time.clock()
        if controlledTime < -0.5:
            # Reset the time reference -- the program is too late, catching up will have perceptible effect on the playback.
            self.reset()
        if controlledTime <= 0:
            controlledTime = 0
        return controlledTime


class Lecteur:
    """
    Gère la lecture d'une vidéo, délègue sont traitement ainsi que son affichage.
    
    Gère la lecture d'une vidéo OpenCV. Instancie un ProcessingTool et lui envoie
    la vidéo frame par frame. Accepte un 
    Permet la mise en pause.
    """
    __slots__ = "cap frameCount height width fps timePerFrame vidDimension".split()
    __slots__ += " jumpEventSubscriber config".split()
    __slots__ += "logger processingTool playbackStatus timeController".split()
    frameIndex = property()

    def getData(self):
        data = self.processingTool.getData()
        return data

    def __init__(self, logger, config, cap, playbackStatus):
        """
        Crée un objet Lecteur à partir d'une video openCV.

        :param logger: Instance utilisée pour afficher les messages metravision.
        :param config: L'objet configuration.
        :param cap: La vidéo à lire.
        """
        self.initVideoInfo(cap)
        self.logger = logger
        self.config = config
        self.jumpEventSubscriber = []

        # Background subtractor initialisation
        self.processingTool = processing.ProcessingTool(
            self.logger,
            processingToolsConfig=config.processingTools,
            vidDimension=self.vidDimension,
            timePerFrame=self.timePerFrame,
            jumpEventSubscriber=self.jumpEventSubscriber,
            segmentDuration=config.lecteur.segmentDuration,
        )

        # Si oui ou non il faut limiter la vitesse de lecture pour ne pas
        # dépasser celle de la vidéo
        speedLimitEnabled = \
            config.lecteur.limitProcessingSpeedToRealVideoSpeed == "always"
        if not config.backgroundMode:
            speedLimitEnabled |= \
                config.lecteur.limitProcessingSpeedToRealVideoSpeed == "auto"
        self.playbackStatus = playbackStatus
        self.timeController = TimeController(self.timePerFrame if speedLimitEnabled else 0)

    def run(self, mvWindow):
        """
        Plays the video, frame by frame, or wait for the video to be unpaused, until end of video or quitting.

        Lit la vidéo image par image ou attends une instruction de l'utilisateur.
        """
        self.timeController.reset()
        while not (self.playbackStatus.endReached or self.playbackStatus.quitting):
            if self.playbackStatus.play or self.playbackStatus.refreshNeeded:
                self.playbackStatus.refreshNeeded = False
                controlledTime = self.timeController.getControlledTime()
                util.timed(mvWindow.waitkey)(controlledTime, self.playbackStatus)

                imageSet = collections.OrderedDict()

                self.playbackStatus.endReached, frame = self.getFrame()
                if self.playbackStatus.endReached:
                    break
                
                imageSet["frame"] = frame
                imageSet["trackers"] = np.array(frame)

                self.processingTool.run(imageSet, self.frameIndex)

                advancementPercentage = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.frameCount
                mvWindow.update(imageSet, advancementPercentage)

                controlledTime = self.timeController.getControlledTime()
                mvWindow.waitkey(controlledTime, self.playbackStatus)
            else:
                duration = 0.05
                mvWindow.waitkey(duration, self.playbackStatus)


    def initVideoInfo(self, cap):
        """Charge dans self les informations liées à la vidéo `cap`."""
        self.cap = cap
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.timePerFrame = 1 / self.fps
        self.vidDimension = (self.height, self.width)


    def jumpTo(self, fraction):
        """Saute à un point de la vidéo, donné comme un nombre entre 0 et 1."""
        frameCount = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frameIndex = int(fraction * frameCount)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
        self.playbackStatus.refreshNeeded = True

        for f in self.jumpEventSubscriber:
            f(cap=self.cap, playbackStatus=self.playbackStatus, frameIndex=frameIndex)

    @frameIndex.getter
    def frameIndex(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)
    
    @frameIndex.setter
    def frameIndex(self, index):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    
    def reachedEnd(self):
        return self.frameIndex >= self.cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1

    def getFrame(self):
        """Renvoie la frame suivante."""
        endReached = False
        notOkCount = 0
        ok = False
        while not ok:
            ok, frame = self.cap.read()
            if not ok:
                if self.reachedEnd():
                    endReached = True
                    break
                notOkCount += 1
                if notOkCount >= 3:
                    self.logger.debug("Not ok >= 3 -- endReached.")
                    endReached = True
                    break
            else:
                notOkCount = 0
        assert frame is not None or endReached
        return endReached, frame
