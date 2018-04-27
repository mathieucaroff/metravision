import numpy as np
import cv2
import math


from util import Namespace, average
"""
Calculate the standard deviation (quantify the amount of dispersion) of an ensemble of data.
"""

def calculSD(li, liref):

    n = len(li)
    m = len(liref)

    x_li = 0
    x_ref = 0

    x_a = average(li)
    x_aref = average(liref)

    x_i = 0
    x_iref = 0

    #Calcul of SD - formula Wikipédia Ecart-type
    for x_i, x_iref in zip(li, liref):
      x_li += x_i ** 2
      x_ref += x_iref ** 2  

    s = ((x_li / n) - x_a ** 2) ** 0.5
    sref = ((x_ref / m) - x_aref ** 2) ** 0.5

    return s, sref

def creeList():

    lt = [1, 1, 1, 1]
    lref = [2, 2, -1, -3]
    sd, sdref = calculSD(lt, lref) #Result expected = 0, 2.12
    print(sd, sdref)


if __name__ == "__main__":
    creeList()