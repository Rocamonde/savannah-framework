import sys
import os

if __name__ == '__main__':
    try:
        from savannah.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Savannah. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    _argv = sys.argv; _argv[0] = os.path.realpath(__file__)
    execute_from_command_line(_argv)
