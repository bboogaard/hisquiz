import functools


def nested_getattr(obj, attr):
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return None
