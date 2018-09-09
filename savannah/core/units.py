from abc import ABC, abstractmethod

from savannah.core import environ, settings
from savannah.core.exceptions import *
from savannah.asynchrony.processes import Process, ProcessManager
from savannah.iounit import CPUServer, Utils as IOUtils
from savannah.sampling.sampler import SamplingManager, Utils as SamplingUtils


# _BaseUnit is the base class for each Unit that must be run.
# All instances that need to be spawned into a different process start with an underscore.
# _BaseUnitProcess is the actual, insulated process.


#
# Abstract Base Classes Definition
#

class _BaseUnit(ABC):
    @abstractmethod
    def init(self):
        pass

class _BaseUnitProcess(Process):
    pass

#
# Main: IOUnit
#

class IOUnit(_BaseUnit):
    """
    Central unit in Savannah. Its incorporated into the main runtime (does not need a ProcessWrapper).
    """
    def __init__(self, host, port, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.server: CPUServer = None
        self.sampling_unit: SamplingUnit = None

    def init(self):
        if not IOUtils.socket_available(self.host, self.port):
            raise RuntimeError('Socket is occupied.')

        # We initialize the SamplingUnit so it can be passed to the interpreter
        self.sampling_unit = SamplingUnit()
        command_interpreter = environ.load_interpreter().CommandInterpreter(self.sampling_unit.manager)
        self.server = CPUServer(self.host, self.port, command_interpreter)

        # Now we start the threads
        self.sampling_unit.init()
        self.server.run()


class SamplingUnit(_BaseUnit):
    def __init__(self):
        self.manager = SamplingManager()

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
        self.manager.propagate(sampler_list)
        self.manager.start_all()

#
# Asynchronous Units:
#

# **Authentication Unit**

class _AuthUnit(_BaseUnit):
    pass

class AuthUnit(_BaseUnitProcess):
    pass

# **Uploader Unit**

class _UploaderUnit(_BaseUnit):
    pass

class UploaderUnit(_BaseUnitProcess):
    pass


# **Local user interface unit**

class LocalUIUnit(_BaseUnit):
    pass





