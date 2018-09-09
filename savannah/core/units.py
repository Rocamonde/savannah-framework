from abc import ABC, abstractmethod

from savannah.iounit import CPUServer, Utils as IOUtils
from savannah.sampling.sampler import SamplingManager, Utils as SamplingUtils
from savannah.core import environ, settings
from savannah.core.exceptions import *


class _Unit(ABC):
    @abstractmethod
    def init(self):
        pass


class IOUnit(_Unit):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server: CPUServer = None

    def init(self):
        if not IOUtils.socket_available(self.host, self.port):
            raise RuntimeError('Socket is occupied.')

        command_interpreter = environ.load_interpreter().CommandInterpreter()
        self.server = CPUServer(self.host, self.port, command_interpreter)
        self.server.run()


class SamplingUnit(_Unit):
    def __init__(self):
        self.manager: SamplingManager = None

    def init(self):
        drivers_module = environ.load_drivers()
        sensor_list = []
        for sensor_name in settings.sensors.enabled_sensors:
            try:
                _sensor = getattr(drivers_module, sensor_name)
                sensor_list.append(_sensor(settings.sensors.custom_settings.get(sensor_name)))
            except AttributeError:
                raise MisconfiguredSettings("Some enabled sensors do not match any object in sensors.py")

        sampler_list = SamplingUtils.make_samplers(sensor_list)
        self.manager = SamplingManager()
        self.manager.propagate(sampler_list)
        self.manager.start_all()
