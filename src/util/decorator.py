import time
from functools import wraps

from util.short import printMV
from util.long import typeVal, glob, show


def identity(x):
    "The identity function. Accepts one parameter and returns it."
    return x


def logged(func, printer = printMV):
    """
    Renvoie une version de la fonction donnée qui affiche les appelles, arguments et valeurs de retour.
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


# Goes together with the decorator util.timed
def printTimes():
    printMV("[:Recorded times totals:]")
    for fname in timed.functionIndex:
        time_ = getattr(timed, fname)
        printMV("Function {fname} ::: {time:.04} seconds".format(fname = fname, time = time_))
