import operator
import contextlib
from functools import wraps
import math
import cv2

import sys
import time

# Simplest functions
def average(iterable):
    """
    Gives the average of the values in the provided iterable.
    """
    return sum(iterable) / max(len(iterable), 1)


def median(iterable):
    values = sorted(iterable)
    le = len(values)
    if le % 2 == 1:
        return values[le // 2 + 1]
    else:
        return (values[le // 2] + values[le // 2 + 1]) / 2


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
    "The 'Do nothing' function. Accepts any kind of parameter and does nothing. Implicitly returns None."
    _ = args, kwargs


def newConstantFunction(val):
    "Returns a function which accepts any kind of parameter, does nothing and returns the value val."
    def constantFunction(*args, **kwargs):
        _ = args, kwargs
        return val
    return constantFunction



# DECORATORS
def identity(x):
    "The identity function. Accepts one parameter and returns it."
    return x


def singleKeyValueFunction(func):
    """
    Transforme une fonction qui prend deux arguments `key` et `value` en une fonction
    qui s'appèle avec la syntax f(key = value), en acceptant un seul paramètre clé-valeur.

    Usage:
        @singleKeyValueFunction
        def f(key, value):
            print(key, ":", value)
        
        >>> f(data = (42, "is the meaning of life"))
        data : (42, 'is the meaning of life')
    """
    @wraps(func)
    def wrapped_func(**kwargs):
        if len(kwargs) != 1:
            raise ValueError(f"Function {func.__name__} accepts a single key-value assignment.")
        key, value = next(iter(kwargs.items()))
        return func(key = key, value = value)
    return wrapped_func


def logged(func, printer = printMV):
    """
    Renvoie une version de la fonction donnée qui affiche les appèles, arguments et valeurs de retour.
    """
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        argString = ", ".join([*map(str, map(typeVal, args)), *(f"{key} = {typeVal(val)}" for key, val in kwargs.items())])
        printer(f"/\\{func.__name__}({argString})")
        res = func(*args, **kwargs)
        printer(f"\\/{func.__name__} ::: {res}")
        return res
    return wrapped_func


def timed(func):
    """
    Decorateur pour chronométrer le temps total passé dans la fonction donnée.
    """
    if func.__name__ not in timed.functionIndex:
        timed.functionIndex.append(func.__name__)
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        beginning = time.time()
        res = func(*args, **kwargs)
        end = time.time()

        try:
            lastTime = getattr(timed, func.__name__)
        except AttributeError:
            lastTime = 0.0
        newTime = lastTime + end - beginning
        timed.__setattr__(func.__name__, newTime)
        return res
    return wrapped_func
timed.functionIndex = []


# https://stackoverflow.com/q/15299878/how-to-use-python-decorators-to-check-function-arguments
# Overall, not so good when used. Prefer the good old-style assert at the beginning of function.
def assertAccepts(*types):
    """Specify the types the arguments of a function must match. Is enforced by assertion."""
    def check_accepts(func):
        #assert len(types) == func.func_code.co_argcount, f"The function {func.__name__} doesn't have the specified number of arguments ({len(types)})."
        # ^ AttributeError: 'function' object has no attribute 'func_code'
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            assert(len(args) + len(kwargs) == len(types))
            for i, (a, t) in enumerate(zip(args, types)):
                assert isinstance(a, t), \
                    f"The {i}th argument of function `{func.__name__}` is expected to be of type `{t}`, but it's value is `{a}`"
            return func(*args, **kwargs)
        return wrapped_func
    return check_accepts


def assertReturns(rtype):
    """Specify the type a function returns. Is enforced by assertion."""
    def check_returns(func):
        @wraps(func)
        def wrapped_func(*args, **kwds):
            retval = func(*args, **kwds)
            assert isinstance(retval, rtype), \
                f"Retval `{retval}` of function `{func.__name__}` is expected to be of type `{rtype}`"
            return retval
        return wrapped_func
    return check_returns


def globbed(gname = None):
    """
    Parameterable decorator to capture the returned value of a function using util.glob.

    Usage:
        @globbed()
        def f(text):
            return "Text> " + text
        
        >>> print(f("Lack of inspiration"))
        Text> Lack of inspiration
        >>> print("Globbed:", glob._f)
        Globbed: Text> Lack of inspiration
        >>> print(f("Information"))
        Text> Information
        >>> print("Globbed:", glob._f)
        Globbed: Text> Information
    """
    def decorator(func):
        name = gname if gname is not None else f"_{func.__name__}"
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            res = func(*args, **kwargs)
            res = glob(**{name: res})
            return res
        return wrapped_func
    return decorator


def shown(func):
    """Decorating make the function show its result when returning."""
    name = f"{func.__name__}( )"
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        res = func(*args, **kwargs)
        res = show(**{name: res})
        return res
    return wrapped_func


def _parameterable_decorator_sample(param):
    _ = param
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            res = func(*args, **kwargs)
            return res
        return wrapped_func
    return decorator


# CLASSES
# Exceptions
class DeveloperInterruption(Exception):
    pass


# Namespace / Dict
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
    __slots__ = []
    def __getattr__(self, key):
        val = dict.__getitem__(self, key)
        if type(val) == dict:
            val = RecursiveReadOnlyDotdict(val)
        return val
    __getitem__ = __getattr__

def test_RecursiveReadOnlyDotdict():
    d = {"a": {"b": {"c": "value"}}, "z": {"y": "nothing"}}
    dd = RecursiveReadOnlyDotdict(d)
    assert dd.a.b.c == "value"
    assert dd.z.y == "nothing"
    assert list(dd.a.b.items()) == [("c", "value")]

    assert dd["a"].b["c"] == "value"
    assert dd["z"].y == "nothing"
    assert list(dd.a["b"].items()) == [("c", "value")]

    assert dd["a"]["b"]["c"] == "value"
    assert dd["z"]["y"] == "nothing"
    assert list(dd["a"]["b"].items()) == [("c", "value")]


# Vector
class ArithmeticList:
    def __init__(self, *args):
        assert args[0] != self
        self.coords = list(args)
    
    def __add__(self, other):
        self._mapOperation(other, operator.add)
    def __sub__(self, other):
        self._mapOperation(other, operator.sub)
    def __mul__(self, scalar):
        self._mapOperation( Point( *([scalar] * len(self.coords)) ), operator.mul )
    def __div__(self, scalar):
        self._mapOperation( Point( *([scalar] * len(self.coords)) ), operator.truediv )
    
    def _mapOperation(self, other, operation):
        assert len(self.coords) == len(other.coords)
        for i in range(len(self.coords)):
            self.coords[i] = operation(self.coords[i], other.coords[i])
    
    def __iter__(self):
        return self.coords.__iter__()


class Vector(ArithmeticList):
    def __init__(self, *args, **kwargs):
        assert not args or not kwargs
        super(Vector, self).__init__(*args)
        for key, val in kwargs.items():
            index = self._indexFromName(key)
            assert index is not None
            coords = self.coords
            l = len(coords)
            if index >= l:
                coords[l:] = [None] * (1 + index - l)
            coords[index] = val
    
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
        assert type(x) == int
        assert type(y) == int
        assert type(width) == int
        assert type(height) == int
        self.x = x
        self.y = y
        self.width = width
        self.height = height

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
    @assertReturns(int)
    def right(self):
        return self.x + self.width

    @bottom.getter
    @assertReturns(int)
    def bottom(self):
        assert type(self.y) == int, typeVal(self.y)
        assert type(self.height) == int
        return self.y + self.height


# CONTEXTE MANAGERS
# https://stackoverflow.com/q/242485/starting-python-debugger-automatically-on-error
@contextlib.contextmanager
def pdbPostMortemUpon(exception):
    try:
        yield
    except exception: # pylint: disable=broad-except
        import pdb, traceback
        traceback.print_exc()
        pdb.post_mortem()


# https://stackoverflow.com/q/242485/starting-python-debugger-automatically-on-error
def interactPostMortem():
    import code, traceback
    _type, _value, tb_ = sys.exc_info()
    traceback.print_exc()
    last_frame = lambda tb=tb_: last_frame(tb.tb_next) if tb.tb_next else tb
    frame = last_frame().tb_frame
    ns = dict(frame.f_globals)
    ns.update(frame.f_locals)
    code.interact(local=ns)


@contextlib.contextmanager
def interactPostMortemUpon(exception = Exception):
    try:
        yield
    except exception: # pylint: disable=broad-except
        interactPostMortem()

@contextlib.contextmanager
def neutralContextManager():
    """This context manager has no effect.

    Usage:
        with neutralContextManager():
            print("The context hasn't changed.")
    """
    yield


# Non Decorators
def typeVal(val):
    """
    Renvoie la représentation sous forme de chaîne de caractère du type de
    la valeur donnée et de la valeur elle-même.

    Si la représentation de la valeur contient plus de trois quatre lignes,
    seul la première et la dernière sont conservées.

    Si la représentation est multiligne ou que la chaine complète fait plus
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


def bboxFromCircle(circle, width_on_height_ratio = 1):
    pi = 3.125
    radius = circle.size / 2
    area = pi * radius ** 2
    width = math.sqrt(width_on_height_ratio * area)
    height = area / width
    x = circle.pt[0] - width / 2
    y = circle.pt[1] - height / 2
    bbox = (int(x), int(y), int(width), int(height))
    return bbox


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
    return value
glob = singleKeyValueFunction(glob)
