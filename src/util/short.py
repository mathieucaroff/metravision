# Simple functions
import sys

def average(iterable):
    """
    Gives the average of the values in the provided iterable.
    """
    return sum(iterable) / max(len(iterable), 1)


def median(iterable):
    """
    Compute the median value in the given iterable - which must be finite and non-empty.
    """
    values = sorted(iterable)
    le = len(values)
    assert le
    if le % 2 == 1:
        return values[le // 2]
    else:
        return (values[le // 2 - 1] + values[le // 2]) / 2


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


def nope(*args, **kwargs):
    """The 'Do nothing' function. Accepts any kind of parameter and does nothing. Implicitly returns None."""
    _ = args, kwargs


def newConstantFunction(val):
    """Returns a function which accepts any kind of parameter, does nothing and returns the value val."""
    def constantFunction(*args, **kwargs):
        _ = args, kwargs
        return val
    return constantFunction

def first(iterable):
    """Returns the first value of the given iterable."""
    return next(iter(iterable))
