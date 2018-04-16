"""
Ajoute une bare de progression de lecture en bas d'une fenêtre.
Permet à l'utilisateur d'aller à n'importe quel point de la vidéo.
"""
# TODO

def setupClickHook(window, jumpToFrameFunction):
    """
    Ajoute un évènement à la fenêtre window qui détècte les clicks dans la partie inférieur de la fenêtre.
    Lors de tels cliques se produisent, execute jumpToFrameFunction
    """

def drawBar(barProperties, buffer, advancementPercentage):
    """
    Dessine une barre horizontale en bas à gauche sur advancementPercentage de l'écran.
    La barre fait barProperties.height pixels de haut et est de couleur barProperties.fgCol (BGR) à gauche,
    et barProperties.bgCol (BGR) à droite.
    """
    height = barProperties.height
    width = buffer.shape[1]
    advancementPx = int(advancementPercentage * width)
    buffer[-height:, :advancementPx, :] = barProperties.fgCol
    buffer[-height:, advancementPx:, :] = barProperties.bgCol

