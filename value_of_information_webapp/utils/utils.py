from boltons.dictutils import FrozenDict

def freeze(obj):
    """
    Source (MIT license): https://github.com/zelaznik/frozen_dict/blob/master/freeze_recursive.py

    Recursive function which turns dictionaries into
    FrozenDict objects, lists into tuples, and sets
    into frozensets.

    Can also be used to turn JSON data into a hasahable value.
    """

    try:
        # See if the object is hashable
        hash(obj)
        return obj
    except TypeError:
        pass

    try:
        # Try to see if this is a mapping
        try:
            obj[tuple(obj)]
        except KeyError:
            is_mapping = True
        else:
            is_mapping = False
    except (TypeError, IndexError):
        is_mapping = False

    if is_mapping:
        frz = {k: freeze(obj[k]) for k in obj}
        return FrozenDict(frz)

    # See if the object is a set like
    # or sequence like object
    try:
        obj[0]
        cls = tuple
    except TypeError:
        cls = frozenset
    except IndexError:
        cls = tuple

    try:
        itr = iter(obj)
        is_iterable = True
    except TypeError:
        is_iterable = False

    if is_iterable:
        return cls(freeze(i) for i in obj)

    msg = 'Unsupported type: %r' % type(obj).__name__
    raise TypeError(msg)
