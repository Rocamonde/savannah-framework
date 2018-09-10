import argparse
from typing import Union
import json

from savannah.sampling import SamplingManager
from savannah.core.exceptions import *
from savannah.core.interpreter import *

__all__ = [
    "CPUInterpreter", "Utils",
]


class CPUInterpreter(AbstractBaseInterpreter):
    def __init__(self, sampling_manager: SamplingManager = None):
        super().__init__()
        self.mapped_commands = {}
        self.verify_data_types = True
        self.sampling_manager = sampling_manager

    def __parse__(self, content: str) -> argparse.Namespace:
        return self.stdparser.parse_args(content.split(' ', 2))

    def __configure__(self):
        """
        Command syntax:
        command --kwargs {JSON-serialized object}

        Data types compatibility: JSON data types.
        We could accept any data type with pickle and a different functioning,
        but that would be a risk if we want to open the port (easily injectable).

        """
        self.stdparser.add_argument('--kwargs', nargs='?')
        self.stdparser.add_argument('command', nargs='?')

    def execute(self, namespace: argparse.Namespace) -> Union[str, UnrecognizedCommandError]:
        try:
            argstr = namespace.kwargs.strip() if namespace.kwargs else str()
            parsed_args = Utils.parse_argstr(argstr) if argstr is not str() else None  # (empty str)
            selected_func: function = self.mapped_commands[namespace.command]

            if not parsed_args:
                return selected_func()

            if not set(parsed_args.keys()) < set(selected_func.__code__.co_varnames):
                raise InvalidArgumentsError

            if self.verify_data_types and \
                    (not all(type(value) is selected_func.__annotations__.get(key)
                             for key, value in parsed_args.items())):
                raise InvalidArgumentsError

            return self.mapped_commands[namespace.command](**parsed_args)

        except json.decoder.JSONDecodeError:
            raise InvalidCommandError

        except KeyError:
            raise UnrecognizedCommandError

    def __getattr__(self, item):
        if item == 'sampling_manager':
            try:
                sm = super().__getattribute__(item)
                if sm is None:
                    raise SamplingUnitNotRunning("SamplingManager attribute not found")
            except AttributeError:
                raise SamplingUnitNotRunning("SampingManager attribute not found")
        return super().__getattribute__(item)


class Utils:
    @staticmethod
    def build_command(command_name, **kwargs):
        return command_name + (' --kwargs {kwargs}'.format(kwargs=Utils.build_argstr(kwargs))
                               if kwargs else '')

    @staticmethod
    def parse_argstr(argstr: str) -> Union[dict, None]:
        return json.loads(argstr)

    @staticmethod
    def build_argstr(kwargs: dict) -> Union[str, None]:
        # Remove None values form build to avoid static type errors
        [kwargs.pop(key) for key in list(kwargs) if kwargs[key] is None]
        # Utiliza list(kwargs) para que haga una copia en memoria y evitar un:
        # ``RuntimeError: dictionary changed size during iteration``
        return json.dumps(kwargs)

