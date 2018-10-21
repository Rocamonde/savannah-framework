import importlib.util
import os
from savannah.core.defaults import drivers, interpreter


def load_module(module_name, file_name=None, file_path=None):
    from savannah.core import settings
    if not (file_name or file_path): raise TypeError("File name or path are required.")
    file_path = file_path or os.path.join(settings.BASEDIR, file_name)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_interpreter() -> interpreter:
    return load_module("interpreter", "interpreter.py")

def load_drivers() -> drivers:
    return load_module("drivers", "drivers.py")
