from abc import ABC, abstractmethod

from savannah.core.decorators import flag_setter

__all__ =  ["Sensor", "PortNotOpenError"]

class PortNotOpenError(Exception):
    # TODO: Implement appropriate error message to raise when port is not open
    pass


class Sensor(ABC):
    """
    Abstract base class for a sensor integration. It can open and close ports, and read
    information from them.
    """

    SENSOR_MAX_FREQUENCY: float = None
    SENSOR_DEFAULT_FREQUENCY: float = None

    MAGNITUDES_VERBOSE: tuple = None

    def __init__(self, settings: dict = None):
        # self.port = None
        self.__is_open = False
        self.settings = settings or dict()

    @property
    def is_open(self):
        return self.__is_open

    @flag_setter('__is_open', True)
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def read(self):
        # TODO: this has to be replaced to allow for overriding
        # TODO: for example, as a wrapper of the actual reading implementation
        # TODO: (this idea could be applied also to issue #3)
        try:
            assert(self.is_open)
            # result = self.port.read()
            # <Method to read from port here>
            # return result
        except AssertionError:
            raise PortNotOpenError
        except:
            # Handle here errors occurring while reading data from the port
            pass

    @flag_setter('__is_open', False)
    @abstractmethod
    def close(self):
        try:
            # self.port.close()
            self.__is_open = False
        except:
            pass
            # Handle here errors occurring while closing the port

    @classmethod
    def name(cls) -> str:
        return cls.__name__
