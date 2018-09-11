import argparse
from typing import Union, Iterable, Mapping, Tuple
from abc import ABCMeta, abstractmethod


__all__ = [
    "AbstractBaseInterpreter", "AbstractBaseCommand",
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

class TypeABI(ABCMeta):
    def __call__(self, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        if hasattr(obj, '__map__'): obj.__map__()
        if hasattr(obj, '__configure__'): obj.__configure__()

        return obj


class AbstractBaseInterpreter(metaclass=TypeABI):
    def __init__(self, *args, **kwargs):
        self.mapped_commands = {}
        self.parser = argparse.ArgumentParser(*args, **kwargs)

    def __map__(self) -> None:
        """
        Create mapping for later execution
        """
        pass

    @abstractmethod
    def __configure__(self):
        """
        Configure parser rules here.
        """
        pass

    def __pre_parse__(self, content: str) -> Iterable:
        raise NotImplementedError
        # We don't want to force its implmenentation for instantiation,
        # just prevent its usage without implementation.

    @abstractmethod
    def __parse__(self, content: Iterable, *args, **kwargs) -> argparse.Namespace:
        """
        Parse all data. Return an argparse.Namespace.
        """
        pass

    @abstractmethod
    def __interpret__(self, namespace: argparse.Namespace) -> Tuple[str, Mapping]:
        """
        Implement the interpretation logic here, and return a execution binding:
        A tuple of two elements: the method_name and a mapping with the kwargs.
        No positional arguments are allowed in bindings (all arguments must be explicit)
        """

    @abstractmethod
    def __execute__(self, method_name: str, kwargs: Mapping):
        """
        Bind mapping here and return type.
        """
        pass

    def run(self, *args, **kwargs):
        return self.__execute__(*self.__interpret__(self.__parse__(*args, **kwargs)))

    def raw_run(self, content):
        return self.run(self.__pre_parse__(content=content))


class AbstractBaseCommand(metaclass=TypeABI):
    def __init__(self, subparsers: argparse._SubParsersAction):
        self.mapped_commands = {}
        self.verbose_name: str = getattr(self.__class__, 'verbose_name', self.__class__.__name__)
        self.help = getattr(self.__class__, 'help', None)
        self.parser = subparsers.add_parser(self.verbose_name, help=self.help)

    @staticmethod
    @abstractmethod
    def action(*args, **kwargs):
        pass

    @abstractmethod
    def __configure__(self):
        pass
