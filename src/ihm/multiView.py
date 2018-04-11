"""
Affiches un nombre arbitraire d'images ou de vidéos dans une fenêtre.
"""
# TODO

def viewDimensionsFromN(n):
    """
    Compute the number of horisontal and vertical views needed to reach at least n views.
    Returns a pair of numbers.
    """
    h = 0
    w = 0
    while True:
        if h * w >= n:
            break
        w += 1
        if h * w >=n:
            break
        h += 1
    return (h, w)

def renderNimages():
    pass

def gatherNimages():
    pass