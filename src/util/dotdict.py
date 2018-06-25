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
    """dot.notation readonly access to dictionary attributes, propagated to children dictionaries upon access."""
    __slots__ = []
    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        if type(val) == dict:
            val = RecursiveReadOnlyDotdict(val)
        return val
    __getattr__ = __getitem__

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
