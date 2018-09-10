from abc import ABC, abstractmethod
import warnings

from savannah.core import environ, settings
from savannah.core.exceptions import *
from savannah.asynchrony.processes import Process, ProcessManager
from savannah.iounit import CPUServer, Utils as IOUtils
from savannah.sampling.sampler import SamplingManager, Utils as SamplingUtils
from savannah.core.extensions.tupperware import unbox


# _BaseUnit is the base class for each Unit that must be run.
# All instances that need to be spawned into a different process start with an underscore.
# _BaseUnitProcess is the actual, insulated process.


#
# Abstract Base Classes Definition
#

class _BaseUnit(ABC):
    @abstractmethod
    def init(self, *args, **kwargs):
        pass

class _BaseUnitProcess(Process):
    pass

class UnitManager(ProcessManager):
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
        self.unit_manager: UnitManager = None

    def init(self):
        if not IOUtils.socket_available(self.host, self.port):
            raise RuntimeError('Socket is occupied.')

        # We initialize the SamplingUnit so it can be passed to the interpreter
        self.sampling_unit = SamplingUnit()
        command_interpreter = environ.load_interpreter().CPUInterpreter(self.sampling_unit.manager)
        self.server = CPUServer(self.host, self.port, command_interpreter)

        # We initialize the UnitManager
        self.unit_manager = UnitManager()
        # We create a space to store the queue proxies to the sensors
        self.unit_manager.sampling_proxies = \
            {k: self.unit_manager.ioserver.Queue() for k in self.sampling_unit.sensor_dict.keys()}

        # Now we start the threads
        self.sampling_unit.init(self.unit_manager.sampling_proxies)
        self.server.run()


class SamplingUnit(_BaseUnit):
    def __init__(self):
        self.manager = SamplingManager()
        self.sensor_dict = {}
        drivers_module = environ.load_drivers()
        for sensor_name in settings.sensors.enabled_sensors:
            try:
                _sensor_obj = getattr(drivers_module, sensor_name)
                self.sensor_dict[sensor_name] = (_sensor_obj(unbox(settings.sensors.custom_settings).get(sensor_name)))
            except AttributeError:
                raise MisconfiguredSettings("Some enabled sensors do not match any object in sensors.py")

        if len(self.sensor_dict.keys()) == 0: warnings.warn("No sensors have been enabled.", RuntimeWarning)

    def init(self, sampling_proxies):
        sampler_list = SamplingUtils.make_samplers(self.sensor_dict.values())
        self.manager.propagate(sampler_list)
        self.manager.start_all(sampling_proxies)

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

