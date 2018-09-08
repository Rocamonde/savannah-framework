from os import path

from savannah.iounit import CPUServer, Utils
from savannah.core import settings, environ

class IOUnit:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server: CPUServer = None

    def init(self):
        if not Utils.socket_available(self.host, self.port):
            raise RuntimeError('Socket is occupied.')

        # samplers = sampler.Utils.samplers([drivers.TorqueSensor(), ])
        # sampling_manager = sampler.SamplerManager(samplers)
        # sampling_manager.start_all()

        command_interpreter = environ.load_interpreter().CommandInterpreter()
        self.server = CPUServer(self.host, self.port, command_interpreter)
        self.server.run()
