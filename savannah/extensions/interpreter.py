import argparse
from typing import Union, Iterable
import json
from abc import ABC, abstractmethod

from savannah.sampling import SamplingManager

__all__ = [
    "AbstractBaseInterpreter",
    "InvalidArgumentsError", "InvalidCommandError", "UnrecognizedCommandError",
    "EvaluationException"
]


#
# Exceptions
#

class EvaluationException(Exception):
    pass


class UnrecognizedCommandError(EvaluationException):
    def __init__(self, *args, **kwargs):
        super(UnrecognizedCommandError, self).__init__(
            'The command specified has not been recognized by the interpreter.',
            *args, **kwargs
        )


class InvalidCommandError(EvaluationException):
    def __init__(self, msg=None, *args, **kwargs):
        msg = 'The command syntax is invalid. ' + (msg or '')
        super(InvalidCommandError, self).__init__(msg, *args, **kwargs)


class InvalidArgumentsError(EvaluationException):
    def __init__(self, *args, **kwargs):
        super(InvalidArgumentsError, self).__init__(
            'The command arguments passed are not valid arguments for the function specified.',
            *args, **kwargs
        )


#
# Classes
#


class AbstractBaseInterpreter(ABC):
    def __init__(self, *args, **kwargs):
        self.stdparser = argparse.ArgumentParser(*args, **kwargs)
        self.__configure__()


    @abstractmethod
    def __parse__(self, content: Union[str, Iterable]) -> argparse.Namespace:
        """
        Pre-process data for stdparser
        """
        pass

    @abstractmethod
    def __configure__(self):
        """
        Configure stdparser here
        """
        pass

    @abstractmethod
    def execute(self, namespace: argparse.Namespace):
        """
        Indicate execution tasks here
        """
        pass

    def interpret(self, content: Union[str, Iterable]):
        self.execute(self.__parse__(content))


class BaseInterpreter(AbstractBaseInterpreter):

    def __parse__(self, content: Iterable) -> argparse.Namespace:
        return self.stdparser.parse_args(content)

    def run(self):
        self.interpret(self.argv)
