from util import average
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


def calculStandardDeviation(data):
    av = average(data)
    n = len(data)
    s = ( sum((val - av) ** 2 for val in data) / (n - 1) ) ** 0.5
    return s


def calculRelativeDifference(data, referenceData):
    relativeDifference = []
    unaccounted = 0
    for (val, refv) in zip(data, referenceData):
        if refv == 0:
            # Skipping, but remembering errors
            unaccounted += val
        else:
            val += unaccounted
            unaccounted = 0
            relDiff = (val - refv) / refv
            relativeDifference.append(relDiff)
    
    return relativeDifference


def _calculRelativeDifferenceStandardDeviation(data, referenceData):
    return calculStandardDeviation(calculRelativeDifference(data, referenceData))



if __name__ == "__main__":
    creeList()