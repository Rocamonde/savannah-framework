__all__ = ["get_basedir", ]

import os
from .exceptions import UndefinedEnvironment

def get_basedir():
    try:
        return os.environ['SAVANNAH_BASEDIR']
    except KeyError:
        raise UndefinedEnvironment("Base directory for Savannah's runtime is not defined.")
