from abc import ABC, abstractmethod

from savannah.asynchrony.processes import Process, ProcessManager
from savannah.core import environ
from savannah.core.exceptions import *
from savannah.core.extensions.tupperware import unbox
from savannah.core.logging import logger
from savannah.iounit import CPUServer, Utils as IOUtils
from savannah.sampling.sampler import SamplingManager, Utils as SamplingUtils

# _BaseUnit is the base class for each Unit that must be run.
# All instances that need to be spawned into a different process start with an underscore.
# _BaseUnitProcess is the actual, isolated process.


#
# Abstract Base Classes Definition
#

# TODO: fix closing. It takes more than that to stop the app appropriately.
# TODO... there should be two closing modes: a clean mode
# TODO... that uploads remaining data, and executes remaining tasks
# TODO... and another that kills the app on the spot.
# TODO... timeout feature is also interesting but be careful because
# TODO... many times after timeout there is no force kill.

class _BaseUnit(ABC):
    @abstractmethod
    def init(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
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
        command_interpreter = environ.load_interpreter().Interpreter(self.sampling_unit.manager)
        self.server = CPUServer(self.host, self.port, command_interpreter)

        # We initialize the UnitManager
        self.unit_manager = UnitManager()
        # We create a space to store the queue proxies to the sensors
        self.unit_manager.sampling_proxies = \
            {k: self.unit_manager.ioserver.Queue() for k in self.sampling_unit.sensor_dict.keys()}

        # Now we start the threads
        self.sampling_unit.init(self.unit_manager.sampling_proxies)
        self.server.run()
        logger.info("IOUnit has been initialized. CPUServer now running at //{0}:{1}".format(self.host, self.port))

    def stop(self):
        self.server.close()
        self.sampling_unit.stop()

class SamplingUnit(_BaseUnit):
    def __init__(self):
        from savannah.core import settings
        self.manager = SamplingManager()
        self.sensor_dict = {}
        drivers_module = environ.load_drivers()
        for sensor_name in settings.sensors.enabled_sensors:
            try:
                _sensor_obj = getattr(drivers_module, sensor_name)
                self.sensor_dict[sensor_name] = (_sensor_obj(unbox(settings.sensors.custom_settings).get(sensor_name)))
            except AttributeError:
                raise MisconfiguredSettings("Some enabled sensors do not match any object in sensors.py")

        if len(self.sensor_dict.keys()) == 0: logger.warning("No sensors have been enabled.")

    def init(self, sampling_proxies):
        sampler_list = SamplingUtils.make_samplers(self.sensor_dict.values())
        self.manager.propagate(sampler_list)
        self.manager.start_all(sampling_proxies)
        logger.info("SamplingUnit has been initialized")


    def stop(self):
        self.manager.stop_all()

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

