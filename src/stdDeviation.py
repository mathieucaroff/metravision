import numpy as np
import cv2
import math


from util import Namespace
"""
Calculate the standard deviation (quantify the amount of dispersion) of an ensemble of data.
"""

def calculSD(Countset):

    n = len(Countset)

    x_a = 0

    #x_a = average(Countset)
    for i in n:
        x_i = Countset[i]
        x_a += x_i

    x_a = x_a / n

    xdiff = 0
    for j in n:
        x_i = Countset[j]

        xdiff += (x_i - x_a) ^ 2

    s = (xdiff / (n - 1)) ^ 0.5

    return s

def creeList():

    lt = [1, 1, 1, 1]
    sd = calculSD(lt)
    print(sd)