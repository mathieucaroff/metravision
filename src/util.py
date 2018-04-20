import operator
import math

import cv2

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

class Point:
    def __init__(self, *args, **kwargs):
        assert not args or not kwargs
        self.coords = list(args)
    
    def __add__(self, other):
        self._mapOperation(other, operator.add)
    def __sub__(self, other):
        self._mapOperation(other, operator.sub)
    def __mul__(self, scalar):
        self._mapOperation( Point( *([scalar] * len(self.coords)) ), operator.mul )
    def __div__(self, scalar):
        self._mapOperation( Point( *([scalar] * len(self.coords)) ), operator.truediv )
    
    def __getattr__(self, name):
        index = self._indexFromName(name)
        return self.coords[index]
    
    def __setattr__(self, name, val):
        index = self._indexFromName(name)
        self.coords[index] = val
    
    def _indexFromName(self, name):
        return {"x": 0, "y": 1, "z": 2}[name]
    
    def _mapOperation(self, other, operation):
        assert len(self.coords) == len(other.coords)
        for i in range(len(self.coords)):
            self.coords[i] = operation(self.coords[i], other.coords[i])


def average(iterable):
    return float(sum(iterable)) / max(len(iterable), 1)


def printMV(*args, **kwargs):
    print("[MV]", *args, **kwargs)


def printMVerr(*args, **kwargs):
    kwargs["file"] = sys.stdout
    printMV(*args, **kwargs)


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

""" 
def drawBbox(frame, bbox, color, *args, **kwargs):
    if not args and not "thickness" in kwargs:
        kwargs["thickness"] = 6
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, color, *args, **kwargs) """

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