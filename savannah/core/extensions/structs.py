from abc import ABCMeta, abstractmethod
from collections import Mapping, UserDict
import json

class ProtectedDict(dict):
    pass

# TODO: improvement proposal: do rollback to previous state before raising error
# TODO: ...in multiple data changes

class StructType(ABCMeta):
    def __call__(self, t: dict = None, **kwargs):

        try:
            assert(not (t and kwargs))
        except AssertionError:
            raise TypeError("Struct() takes no args or no kwargs")

        target = t or kwargs

        if not (isinstance(target, Mapping) or
                isinstance(target, ProtectedDict)):
            return target

        return super().__call__(t, **kwargs)


class _StructBase(metaclass=StructType):
    def __init__(self, t: dict, **kwargs):
        target: dict = t or kwargs
        self.__setattr__('__struct__', dict(), _init=True)
        for key, value in target.items():
            self.__setattr__(key, self.__class__(value), _init=True)

    def __setattr__(self, key, value, _init=False):
        if key == '__struct__':
            if not isinstance(value, dict):
                raise TypeError("Cannot assign to __struct__: type is not dict")
            self.__rs__(value)

        elif key not in self.__dict__.keys():
            if not self.__class__.immutable or _init:
                if not key.startswith('__'):
                    self.__struct__[key] = value
                else:
                    raise AttributeError("Cannot assign to {key}: unrecognised key starts with '__'")
            else:
                raise AttributeError("Cannot assign {value} to {key}: {class_name} is not mutable"
                                     .format(value=value, key=key, class_name=self.__class__.__name__))

        # We also store it in the __dict__ to allow for auto-completion
        super().__setattr__(key, value)

    def __getattr__(self, item):
        if item in ('__dict__', '__struct__'):
            return super().__getattribute__(item)
        elif item in self.__dict__.keys():
            return self.__dict__[item]
        elif item in self.__struct__.keys():
            return self.__struct__[item]
        else:
            raise AttributeError("attribute does not exist")

    @staticmethod
    def __unwrap__(obj: '_StructBase'):
        if not isinstance(obj, _StructBase):
            return obj

        d = {}
        for key, val in obj.__struct__.items():
            d[key] = _StructBase.__unwrap__(val)
        return d

    @property
    def __as_dict__(self):
        return self.__unwrap__(self)

    def __rs__(self, new_val: dict):
        # To execute this method, __struct__ cannot have been replaced yet.
        _changed = []
        for k,v in new_val.items():
            if k in self.__struct__.keys():
                _changed.append(k)
            self.__setattr__(k, v)

        del k,v
        for k in self.__struct__.keys():
            if k not in _changed:
                self.__dict__.pop(k)

    def __repr__(self) -> str:
        _repr = ', '.join(('='.join((k, v.__repr__())) for k, v in self.__struct__.items()))
        return 'Struct({})'.format(_repr)

    def __str__(self, indent: int = 4) -> str:
        return json.dumps(self.__as_dict__, indent=indent).replace('{', self.__class__.__name__+'{')


class Struct(_StructBase):
    """
    Mutable (default) Struct
    """
    immutable = False



class ImmutableStruct(_StructBase):
    """
    Immutable Struct.
    In reality, only self.__struct__ AND its content
    are protected against modification.
    """
    immutable = True


# TODO: if we change __struct__ to None, previously defined attributes are returned
# TODO ...but new ones don't work
# TODO: first fix this, and then check the __struct__ assignment to be a dict or raise a TypeError
# If no fix is found, merge struct and struct base and make ImmutableStruct an alias function that passes an
# immutable bool to instantiation
