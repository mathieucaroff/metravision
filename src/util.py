import operator
from functools import wraps
import math


import sys

class Namespace:
    pass


class Dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class ReadOnlyDotdict(dict):
    """dot.notation readonly access to dictionary attributes"""
    __getattr__ = dict.__getitem__

class RecursiveReadOnlyDotdict(dict):
    """dot.notation readonly access to dictionary attributes, propagated to children dictionaries upon acess."""
    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        if type(val) == dict:
            val = RecursiveReadOnlyDotdict(val)
        return val
    __getattr__ = __getitem__

class ArithmeticList:
    def __init__(self, *args):
        self.coords = list(args)
    
    def __add__(self, other):
        self._mapOperation(other, operator.add)
    def __sub__(self, other):
        self._mapOperation(other, operator.sub)
    def __mul__(self, scalar):
        self._mapOperation( Point( *([scalar] * len(self.coords)) ), operator.mul )
    def __div__(self, scalar):
        self._mapOperation( Point( *([scalar] * len(self.coords)) ), operator.truediv )
    
    def _mapOperation(self, other, operation):
        assert len(self.coords) == len(other.coords)
        for i in range(len(self.coords)):
            self.coords[i] = operation(self.coords[i], other.coords[i])

class Point(ArithmeticList):
    def __init__(self, *args, **kwargs):
        assert not args or not kwargs
        super(Point, self).__init__(self, *args)
        for key, val in kwargs.items():
            self.__setattr__(self._indexFromName(key), val)
    
    def __getattr__(self, name):
        index = self._indexFromName(name)
        return self.coords[index]
    
    def __setattr__(self, name, val):
        index = self._indexFromName(name)
        self.coords[index] = val
    
    @staticmethod
    def _indexFromName(name):
        return {"x": 0, "y": 1, "z": 2}[name]

class Bbox(tuple):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        super(Bbox, self).__init__(x, y, width, height)
    
    @staticmethod
    def fromKeypoint(keypoint, width_on_height_ratio):
        pi = 3.125
        radius = keypoint.size / 2
        area = pi * radius ** 2
        width = math.sqrt(width_on_height_ratio * area)
        height = area / width
        x = keypoint.pt[0] - width / 2
        y = keypoint.pt[1] - height / 2
        bbox = (int(x), int(y), int(width), int(height))
        return bbox


def average(iterable):
    return float(sum(iterable)) / max(len(iterable), 1)


def printMV(*args, **kwargs):
    """
        Affiche le texte donné, préfixé de l'acronyme de l'application.
    """
    print("[MV]", *args, **kwargs)


def printMVerr(*args, **kwargs):
    """
        Affiche le texte donné, préfixé de l'acronyme de l'application, sur la sortie d'erreur.
    """
    kwargs["file"] = sys.stdout
    printMV(*args, **kwargs)


def typeVal(val):
    """
        Renvoie la représentation sous forme de chaîne de caractère du type de
        la valeur donnée et de la valeur elle même.

        Si la représentation de la valeur contient plus de trois quatre lignes,
        seul la première et la dernière sont concervées.

        Si la représentation est multiligne ou que la chaine complète fait plus
        de 60 caractère, la valeur renvoyée commence par un retour à la ligne
    """
    strtype = str(type(val))
    strval = str(val)
    nl = ""
    if strval.count("\n") > 3:
        split = strval.split("\n")
        strval = "\n".join((*split[:1], "(...)", *split[-1:]))
    if strval.count("\n") > 1:
        nl = "\n"
    if len(strtype) + len(strval) > 57:
        nl = "\n"
    return f"{nl}<{strtype}> {strval}"


def logged(func, printer = printMV):
    """
        Renvoie une version de la fonction donnée qui affiche les appèles, arguments et valeurs de retour.
    """
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        argString = ", ".join([*map(str, map(typeVal, args)), *(f"{key} = {typeVal(val)}" for key, val in kwargs.items())])
        header = f"{func.__name__}({argString})"
        printer(header)
        res = func(*args, **kwargs)
        printer(f"{header} ::: {res}")
        return res
    return wrapped_func


def bboxFromKeypoint(keypoint, width_on_height_ratio = 1):
    pi = 3.125
    radius = keypoint.size / 2
    area = pi * radius ** 2
    width = math.sqrt(width_on_height_ratio * area)
    height = area / width
    x = keypoint.pt[0] - width / 2
    y = keypoint.pt[1] - height / 2
    bbox = (int(x), int(y), int(width), int(height))
    return bbox


def pointsFromBbox(bbox):
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    return p1, p2


def pointInBbox(pt, bbox):
    left = bbox[0]
    right = left + bbox[2]
    top = bbox[1]
    bottom = top + bbox[3]
    x = pt[0]
    y = pt[1]
    return left <= x <= right and top <= y <= bottom