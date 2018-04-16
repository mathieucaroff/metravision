import numpy
import cv2

print(cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5)))

print(cv2.getStructuringElement(cv2.MORPH_CLOSE, (5,5)))

# print(cv2.createMorphlogyFilter(cv2.MORPH_CLOSE, (5,5)))

print(cv2.__version__)