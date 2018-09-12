from typing import Any

def flag_setter(flag: str, value: Any):
    """Sets a flag attribute contained in self to the value specified after execution"""

    def decorator(func):
        def wrapper(self: object, *args, **kwargs):
            func(*args, **kwargs)
            self.__setattr__(flag, value)

        return wrapper

    return decorator