import cv2

"""
Ajoute une bare de progression de lecture en bas d'une fenêtre.
Permet à l'utilisateur d'aller à n'importe quel point de la vidéo.
"""

def setupClickHook(mouseCallbackList, bufferShape, sensitivityHeight, jumpToFrameFunction):
    """
    Ajoute un évènement à la fenêtre window qui détècte les clicks dans la partie inférieur de la fenêtre.
    Lors de tels cliques se produisent, execute jumpToFrameFunction
    """
    height, width = bufferShape
    def evListener(event, x, y, flags, param):
        _ = flags, param
        if event == cv2.EVENT_LBUTTONDOWN:
            if y > height - sensitivityHeight:
                jumpToFrameFunction(x / width)
    
    mouseCallbackList.append(evListener)

def drawBar(progressBarConfig, width, buffer, advancementPercentage):
    """
    Dessine une barre horizontale en bas à gauche sur advancementPercentage de l'écran.
    La barre fait progressBarConfig.height pixels de haut et est de couleur progressBarConfig.fgColor (BGR) à gauche,
    et progressBarConfig.bgColor (BGR) à droite.
    """
    height = progressBarConfig.height
    advancementPx = int(advancementPercentage * width)
    buffer[-height:, :advancementPx, :] = progressBarConfig.fgColor
    buffer[-height:, advancementPx:, :] = progressBarConfig.bgColor

