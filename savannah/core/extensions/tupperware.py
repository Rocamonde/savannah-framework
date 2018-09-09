from collections import UserDict
import collections
from typing import NamedTuple, TypeVar
import copy

__author__ = 'github.com/hangtwenty, github.com/Rocamonde'


def box(mapping):

    # This prevents in-place change of original object
    _mapping = copy.deepcopy(mapping)

    if (isinstance(_mapping, collections.Mapping) and
            not isinstance(_mapping, ProtectedDict)):
        for key, value in _mapping.items():
            _mapping[key] = box(value)
        return namedtuple_from_mapping(_mapping)
    return _mapping


def namedtuple_from_mapping(mapping, name="Box"):
    this_namedtuple_maker = collections.namedtuple(name, mapping.keys())
    return this_namedtuple_maker(**mapping)

Box = TypeVar('Box', bound=NamedTuple)

class ProtectedDict(UserDict):
    """ A class that exists just to tell `box` not to eat it.
    `box` eats all dicts you give it, recursively; but what if you
    actually want a dictionary in there? This will stop it. Just do
    ProtectedDict({...}) or ProtectedDict(kwarg=foo).
    """


def box_from_kwargs(**kwargs):
    return box(kwargs)

def is_nt_instance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple: return False
    f = getattr(t, '_fields', None)
    if not isinstance(f, tuple): return False
    return all(type(n)==str for n in f)

def unbox(nt: NamedTuple):
    if not is_nt_instance(nt): return nt
    d = nt._asdict()
    unboxed = dict()
    for key, val in d.items():
        if is_nt_instance(val):
            val = unbox(val)
        unboxed[key] = val
    return unboxed
