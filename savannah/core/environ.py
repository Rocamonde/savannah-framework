import importlib.util
from os import path
from savannah.core import settings
from savannah.core.neutral import drivers, interpreter


def load_module(module_name, file_name=None, path=None):
    if not (file_name or path): raise TypeError("File name or path are required.")
    path = path or path.join(settings.BASEDIR, file_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_interpreter() -> interpreter:
    return load_module("interpreter", "interpreter.py")

def load_drivers() -> drivers:
    return load_module("drivers", "drivers.py")
