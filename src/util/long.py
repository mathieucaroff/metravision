# Long functions

from util.short import nope, printMV


# Not a decorator, but useful to make some.
def singleKeyValueFunction(func):
    """
    Transforme une fonction qui prend deux arguments `key` et `value` en une fonction
    qui s'appelle avec la syntax f(key = value), en acceptant un seul paramètre clé-valeur.

    Usage:
        @singleKeyValueFunction
        def f(key, value):
            print(key, ":", value)
        
        >>> f(data = (42, "is the meaning of life"))
        data : (42, 'is the meaning of life')
    """
    from functools import wraps
    @wraps(func)
    def wrapped_func(**kwargs):
        if len(kwargs) != 1:
            raise ValueError(f"Function {func.__name__} accepts a single key-value assignment.")
        key, value = next(iter(kwargs.items()))
        return func(key = key, value = value)
    return wrapped_func


# Decorators
def typeVal(val):
    """
    Renvoie la représentation sous forme de chaîne de caractère du type de
    la valeur donnée et de la valeur elle-même.

    Si la représentation de la valeur contient plus de trois quatre lignes,
    seul la première et la dernière sont conservées.

    Si la représentation est multiligne ou que la chaîne complète fait plus
    de 60 caractères, la valeur renvoyée commence par un retour à la ligne.
    """
    strval = repr(val)

    # Type
    if strval[0] == "<" and strval[-1] == ">":
        strtype = ""
    else:
        strtype = repr(type(val))
    
    # Newline(s)
    nl = ""
    if strval.count("\n") > 3:
        split = strval.split("\n")
        strval = "\n".join((*split[:1], "(...)", *split[-1:]))
    if strval.count("\n") > 1:
        nl = "\n"
    
    if len(strtype) + len(strval) > 57:
        nl = "\n"
    return f"{nl}<{strtype}> {strval}"


def callbackProperty(localName, getCallback = nope, setCallback = nope):
    def fget(self):
        getCallback(self)
        return getattr(self, localName)
    def fset(self, val):
        setattr(self, localName, val)
        setCallback(self, val)
    return property(fget = fget, fset = fset)


def pointInBbox(pt, bbox):
    left = bbox[0]
    right = left + bbox[2]
    top = bbox[1]
    bottom = top + bbox[3]
    x = pt[0]
    y = pt[1]
    return left <= x <= right and top <= y <= bottom


def show(key, value):
    """
    Save the given value at the given key, to the `globbed` object for interactive inspection and debbuging.
    The function will raise a ValueError if used with more than one keyword argument. It will also do so if used with less than one.

    Usage:
        >>> import util
        >>> data = util.show(gdata = [("green", "foo"), ("orange", "bar")])
        gdata :: [("green", "foo"), ("orange", "bar")]
        > None
        >>> data == [("green", "foo"), ("orange", "bar")]
        > True
    """
    printMV(key, "::", value)
    return value
show = singleKeyValueFunction(show)


def showTypeVal(key, value):
    printMV(key, "::", typeVal(value))
showTypeVal = singleKeyValueFunction(showTypeVal)


def glob(key, value):
    """
    Save the given value at the given key, to the `globbed` object for interactive inspection and debbuging.
    The function will raise a ValueError if used with more than one keyword argument. It will also do so if used with less than one.

    Usage:
        In .py file::
            import util
            data = util.glob(gdata = [("green", "foo"), ("orange", "bar")])

        Then in interactive console::
            >>> import util
            >>> print(globbed.gdata)
            [("green", "foo"), ("orange", "bar")]
    """
    glob.__setattr__(key, value)
    if key not in glob.valIndex:
        glob.valIndex.append(key)
    return value
glob = singleKeyValueFunction(glob)
glob.valIndex = []
