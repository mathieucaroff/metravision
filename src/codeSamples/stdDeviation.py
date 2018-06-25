from util import average


def calculSD(li, liref):
    """
    Calcul de l'écart-type (quantifier le montant de la dispersion) de deux ensembles de données.

    :param list li: une liste de valeurs qu'a été identifie par le logiciel
    :param list liref: liste de valeurs de référence pour les valeurs étudiées
    :return: l'écart-type des valeurs étudiées et des valeurs de référence respectivement
    :rtype: (float, float)
    
    """
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
    """
    Créer deux listes pour tester la fonction calculSD. Imprimer les résultats du deux écart-types
    
    """

    lt = [1, 1, 1, 1]
    lref = [2, 2, -1, -3]
    sd, sdref = calculSD(lt, lref) #Result expected = 0, 2.12
    print(sd, sdref)


def calculStandardDeviation(data):
    """
    Calculer l'écart-type d'un ensemble de données.

    :param list data: liste de valeurs
    :return: l'écart-type de l'ensemble de valeurs
    :rtype: float
    
    """
    av = average(data)
    n = len(data)
    s = ( sum((val - av) ** 2 for val in data) / (n - 1) ) ** 0.5
    return s


def calculRelativeDifference(data, referenceData):
    """
    Calculer la différence relative entre les valeurs pour être analysées et une référence, saut les valeurs de référence égales à zero et mettre tous les individuels différences dans une liste.


    :param list data: liste des valeurs pour être analysée.
    :param list referenceData: liste des valeurs de référence
    :return: différence relative entre les valeurs
    :rtype: list
    
    """
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
    """
    Calcul de l'écart-type (quantifier le montant de la dispersion) de la différence relative entre deux ensembles de données.

    :param list data: liste des valeurs pour être analysée 
    :param list referenceData: lists des valeurs de référence
    :return: l'écart-type de la différence relative
    :rtype: float
    
    """
    return calculStandardDeviation(calculRelativeDifference(data, referenceData))



if __name__ == "__main__":
    creeList()