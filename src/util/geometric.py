import math
import operator

import numpy as np
import cv2

from util.long import typeVal

class ArithmeticList:
    def __init__(self, *args):
        self.coords = list(args)
    
    def __add__(self, other):
        return self._mapOperation(other, operator.add)
    def __sub__(self, other):
        return self._mapOperation(other, operator.sub)
    def __mul__(self, scalar):
        return self._mapOperation( ArithmeticList( *([scalar] * len(self.coords)) ), operator.mul )
    def __div__(self, scalar):
        return self._mapOperation( ArithmeticList( *([scalar] * len(self.coords)) ), operator.truediv )
    
    def _mapOperation(self, other, operation):
        assert len(self.coords) == len(other.coords)
        return ArithmeticList(operation(x, y) for (x, y) in zip(self.coords, other.coords))
    
    def __iter__(self):
        return self.coords.__iter__()


class Vector(ArithmeticList):
    def __init__(self, *args, **kwargs):
        assert not args or not kwargs
        super(Vector, self).__init__(*args)
        for key, val in kwargs.items():
            index = self._indexFromName(key)
            assert index is not None
            l = len(self.coords)
            if index >= l:
                self.coords[l:] = [None] * (1 + index - l)
            self.coords[index] = val
        assert None not in self.coords
    
    def __getattr__(self, name):
        index = self._indexFromName(name)
        if index is not None:
            return self.coords[index]
        else:
            return object.__getattribute__(self, name)
    
    def __setattr__(self, name, val):
        index = self._indexFromName(name)
        if index is not None:
            self.coords[index] = val
        else:
            object.__setattr__(self, name, val)
    
    def quadnorm(self):
        return sum(v ** 2 for v in self.coords)
    
    def norm(self):
        return math.sqrt(self.quadnorm())
    
    @staticmethod
    def _indexFromName(name):
        try:
            return {"x": 0, "y": 1, "z": 2}[name]
        except KeyError:
            return None


# More geometric objects
class Point(Vector):
    pass


# OpenCV-like keypoint
class Keypoint:
    __slots__ = "pt size".split()


class Circle(Point):
    pi = math.pi
    def __init__(self, x, y, r):
        """
        A Circle is a point with a size associated -- here r is the radius.
        """
        super().__init__(x, y)
        self.r = r
    
    @classmethod
    def fromBbox(cls, bbox):
        pi = 3.125
        radius = math.sqrt(bbox.area / pi)
        x, y = bbox.center
        return cls(x, y, radius)
    
    @classmethod
    def fromKeypoint(cls, keypoint):
        radius = keypoint.size / 2
        x = keypoint.pt[0]
        y = keypoint.pt[1]
        return cls(x, y, radius)
    
    def __contains__(self, point):
        return (self - point).quadnorm() < self.r
    
    def isInside(self, otherCircle):
        return (self - otherCircle)
    
    @property
    def center(self):
        return Point(self.x, self.y)
    
    @property
    def area(self):
        return self.pi * self.r ** 2


class MvBbox:
    area, bbox, center, right, bottom = [ property() ] * 5
    __slots__ = "x y width height".split()

    def __init__(self, x, y, width, height):
        """
        A bbox is a bounding box. (x, y) are it's top left corner coordinates.

        It is defined by the coordinates of the top left corner and the size of the box (width, height).

        It has properties:
        bbox:: This property is simpler than the MvBbox object: it's a tuple carrying no methode.
        area:: 
        center::
        bottom::
        right::
        """
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    @staticmethod
    def fromCircle(circle, width_on_height_ratio):
        area = circle.area
        width = math.sqrt(width_on_height_ratio * area)
        height = area / width
        x = circle.x - width / 2
        y = circle.y - height / 2
        bbox = (int(x), int(y), int(width), int(height))
        return bbox
    
    def __contains__(self, point):
        dx = point.x - self.x
        dy = point.y - self.y
        return  0 <= dx <= self.width  and  0 <= dy <= self.height
    
    def isInside(self, otherBbox):
        """Tells whether a bbox is strictly inside another"""
        left = self.x <= otherBbox.x
        top = self.y <= otherBbox.y
        right = self.x + self.width >= otherBbox.x + otherBbox.width
        bottom = self.y + self.height >= otherBbox.y + otherBbox.height
        return all([left, top, right, bottom])

    def extractFrom(self, frame, fillerColor=None):
        """
        Accept a frame and extract the region correspondig to mvbbox from it.

        If the region falls outside the frame, use the fillerColor

        :param frame: The frame from which to extract the region.
        :param fillerColor:
            The color to use to fill the extracted image if the region is
            partially or totally out of the frame. Black by default.
        """
        if len(frame.shape) < 2 or frame.shape[0] <= 0 or frame.shape[1] <= 0:
            raise ValueError(f"Given frame's dimension are nul. shape: {frame.shape}")
        if fillerColor is not None:
            fillerValue = fillerColor
        else:
            fillerValue = frame[0, 0]
            fillerValue.fill(0)

        _fh, fw = frame.shape[:2]

        destShape = [self.height, self.width, *frame.shape[2:]]
        destination = np.empty(shape = destShape, dtype = frame.dtype)
        destination.fill(fillerValue)

        # x and y (included) and xx and yy (excluded) are the bounaries of the
        # destination area where the part of the frame will be copied.
        x, y = 0, 0
        xx, yy = self.width, self.height
        # sx and sy (included) and right and bottom (excluded) are the bounaries
        # of the part of the frame which will be copied.
        sx, sy = self.x, self.y
        right, bottom = self.right, self.bottom
        if self.x < 0:
            x -= self.x
            sx -= self.x # sx == 0
        if self.y < 0:
            y -= self.y
            sy -= self.y # sy == 0
        if self.right > fw:
            xx -= self.right
            right -= self.right
        if self.bottom > fw:
            yy -= self.bottom
            bottom -= self.bottom

        destination[x : xx, y : yy] = frame[sx : right, sy : bottom]
        return destination
    
    def draw(self, frame, color, *args, **kwargs):
        if len(args) == 0 and "thickness" not in kwargs:
            kwargs["thickness"] = 6
        cv2.rectangle(frame, (self.x, self.y), (self.right, self.bottom), color, *args, **kwargs)


    @bbox.getter
    def bbox(self):
        return (self.x, self.y, self.width, self.height)

    @bbox.setter
    def bbox(self, val):
        self.x, self.y, self.width, self.height = map(int, val)


    @area.getter
    def area(self):
        return self.width * self.height

    @center.getter
    def center(self):
        return Point(self.x + self.width // 2, self.y + self.height // 2)

    @right.getter
    def right(self):
        return self.x + self.width

    @bottom.getter
    def bottom(self):
        assert type(self.y) == int, typeVal(self.y)
        assert type(self.height) == int
        return self.y + self.height