import contextlib

@contextlib.contextmanager
def neutralContextManager():
    """This context manager has no effect.

    Usage:
        with neutralContextManager():
            print("The context hasn't changed.")
    """
    yield


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
    import code, traceback, sys
    _type, _value, tb_ = sys.exc_info()
    traceback.print_exc()
    last_frame = lambda tb=tb_: last_frame(tb.tb_next) if tb.tb_next else tb
    frame = last_frame().tb_frame
    ns = dict(frame.f_globals)
    ns.update(frame.f_locals)
    code.interact(local=ns)


@contextlib.contextmanager
def interactPostMortemUpon(exception=Exception):
    try:
        yield
    except exception: # pylint: disable=broad-except
        interactPostMortem()

