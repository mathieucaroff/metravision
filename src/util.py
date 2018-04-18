import operator

import sys

class Namespace:
    pass


class Dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class ReadOnlyDotdict(dict):
    """dot.notation readonly access to dictionary attributes"""
    __getattr__ = dict.get

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