from abc import ABCMeta, abstractmethod

#
# Decorated Class
#

class _DecoratedType(type):

    def __new__(type, *args, **kwargs):
        cls = super().__new__(type, *args, **kwargs)
        if hasattr(cls, '__decors__'):
            for i, el in cls.__dict__.items():
                if hasattr(el, '__decorated__'):
                    cls.__decors__[i] = el.__decorated__
        else:
            raise AttributeError("Class must have __decors__ attribute")
        return cls


class Decorated(metaclass=_DecoratedType):
    __decors__ = {}

    def __new__(cls, *args, **kwargs):
        for i, el in cls.__decors__.items():
            decorated_el = el(getattr(cls, i))
            setattr(cls, i, decorated_el)
        return super().__new__(cls, *args, **kwargs)


#
# Decorator
#


class _DecoratorType(ABCMeta):
    def __call__(self, *args, **kwargs):
        try:
            obj = super().__call__(*args, **kwargs)
        except NotImplementedError:
            # __init__ takes no arguments:
            obj = super().__call__(__bypass__=True)
            obj.__call__(*args, **kwargs)
        return obj


class Decorator(metaclass=_DecoratorType):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('__bypass__', False):
            raise NotImplementedError

    def __call__(self, unbound_method):
        setattr(unbound_method, '__decorated__', self.__wrapper__)
        return unbound_method


    @abstractmethod
    def __wrapper__(self, wrapped_bound_method):
        from functools import wraps
        @wraps(wrapped_bound_method)
        def wrapper(*args, **kwargs):
            # Do something here
            return wrapped_bound_method(*args, **kwargs)
        return wrapper

#
# Implementations
#


class flag(Decorator):
    def __init__(self, flag_name, flag_val):
        self.flag_name = flag_name
        self.flag_val = flag_val

    def __wrapper__(self, wrapped_method):
        from functools import wraps
        @wraps(wrapped_method)
        def wrapper(obj: object, *args, **kwargs):
            obj.__setattr__(self.flag_name, self.flag_val)
            return wrapped_method(obj, *args, **kwargs)

        return wrapper
