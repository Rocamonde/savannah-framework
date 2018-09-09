import multiprocessing_on_dill as mp
from multiprocessing_on_dill import managers as _iomanagers
from abc import abstractmethod
# from multiprocessing import managers as _iomanagers
# import multiprocessing_on_dill.connection
# import multiprocessing.connection

from .base import *
from .pipes import *


__all__ = [
    "Process", "EasyProcess", "ProcessManager", "ReverseProcessManager"
]


"""
Process
"""


class Process(AsyncWrapper):

    def __init__(self,
                 is_daemon: bool = False,
                 manager: 'ProcessManager' = None,
                 # enable_inbox: bool = False,
                 name: str = None,
                 ) -> None:

        super().__init__(is_daemon=is_daemon, name=name)
        self.__process: mp.Process = None

        self.manager: 'ProcessManager' = None  # Add support for subclass custom annotation
        if manager:
            self.implement_manager(manager=manager)

        # TODO: fix for this
        """
        self.__inbox: mp.Queue = None
        self.__inbox_enabled: bool = False
        if enable_inbox: self.enable_inbox()
        """

    def start(self, **kwargs):

        if self.manager:
            # The namespace is where all proxy references to mp.managers.SyncManager objects are stored
            if self.manager.ioserver_enabled: kwargs['namespace'] = self.manager.namespace
            # Pipes are connective pathways created independently of the manager
            # and let read and dump raw bytes on either end.
            kwargs['pipe_map'] = self.manager.pipe_network.get_pipes(self.name)

        self.__process = mp.Process(target=self.fetch_target(),
                                    kwargs=kwargs,
                                    name=self.name)

        self.__process.daemon = self.is_daemon  # Daemonize thread
        try:
            self.__process.start()  # Start the execp
        except TypeError as exc:
            raise TypeError("A TypeError while starting the process has occurred."
                            "Have you forgot to decorate the task with @staticmethod?") from exc

    def wait(self, timeout=None) -> bool:
        """Thought to be used as: `try: if self.wait(): STMT; STMT; except: STMT`"""
        self.process.join(timeout)
        if self.process.exitcode is None:
            return False
        elif self.process.exitcode is 0:
            return True
        else:
            return self.process.exitcode

    @property
    def is_running(self) -> bool:
        return self.process.is_alive() if self.process else False

    @property
    def process(self) -> mp.Process:
        return self.__process

    """
    Replace task method with a static method:
    """

    # Rationale:
    # ----------
    # In threads, direct references to objects are possible.
    # For this reason, we can make a thread of an instance method that is passed
    # `self` as a first argument without any problem.
    # However, processes cannot share memory, and to emulate "memory reference"
    # What is done is to actually duplicate objects and create copies of them.
    # Elements that require to be updated either use a pipe or a background server
    # which in turn uses pipes/sockets.
    #
    # If we try to pickle the method to pass to the process, and `self` contains
    # a reciprocal reference to a manager, `pickle`-ing will be unsuccessful
    # because it will join an infinite loop: pickling self will imply pickling the
    # reference to the manager, which in turn contains a reference to self, and so.
    # (Pickle does not yet let serialization of objects that have a cross-reference).
    # For this reason, method has to be static (this is, be stored as a class variable).

    @staticmethod
    @abstractmethod
    def task(**kwargs):
        pass

    """
    Features
    """

    # TODO: this approach does not work. Pipes are not pickle-able.
    # TODO: ...set a proxy reference to the Queue.
    """
    def enable_inbox(self) -> 'Process':

        self.__inbox = mp.Queue()
        self.__inbox_enabled = True
        return self

    @property
    def inbox_enabled(self) -> bool:
        return self.__inbox_enabled

    @property
    def inbox(self) -> mp.Queue:
        \"\"\"
        Private inbox to communicate exclusively with the process.
        Differs with ProcessManager.queue in that the latter is shared
        (common for all processses) and the former is not.
        \"\"\"
        return self.__inbox
    """


"""
ProcessManager
"""


class _IOManager(_iomanagers.SyncManager):
    pass


class ProcessManager(Manager):

    def __init__(self,
                 enable_ioserver: bool = True,
                 ) -> None:

        super().__init__()

        # Features
        self._iomanager: _IOManager = None
        self.__namespace: _iomanagers.Namespace = None
        self.__pipe_network = PipeNetwork()

        # Flags
        self.__ioserver_enabled = False

        # Features init
        if enable_ioserver: self.enable_ioserver()

    # Replacement to get dynamic suggestions
    def find_by_name(self, name: str) -> Process: return super().find_by_name(name=name)

    def find_by_process(self, process: mp.Process) -> Process:
        try:
            # Utilizar el propio método facilita el manejo de excepciones
            return self.find_by_name(process.name)
        except AttributeError:
            raise WrapperTypeError

    """
    Communication-related methods
    """

    # Enabler methods are thought to be chained. Hence them returning self.

    def enable_ioserver(self) -> 'ProcessManager':
        self._iomanager = _IOManager()
        self._iomanager.start()
        self.__namespace = self._iomanager.Namespace()
        self.__ioserver_enabled = True
        return self

    @property
    def ioserver(self) -> _IOManager:
        """
        The ioserver lets extend the conventional mp.Queue and mp.Pipe types,
        e.g. creating a namespace that is shared.
        This functionality is required to enable the capabilities of the analogous
        manager object found for Threads.
        """
        return self._iomanager

    @property
    def namespace(self) -> _iomanagers.Namespace:
        """
        Return a proxy for the shared Namespace object.
        """
        # It cannot set self.__namespace,
        # but it can function as a setter to the namespace variables.
        return self.__namespace

    @property
    def ioserver_enabled(self): return self.__ioserver_enabled

    """
    Pipes
    """

    @property
    def pipe_network(self) -> PipeNetwork:
        return self.__pipe_network

"""
Utils
"""


class EasyProcess(Process):
    """
    Shortcut for creating processes without having to inherit from `Process`,
    for cases where little or no extension is needed.
    Map a function to the .start method and run the Process naturally.

    It allows chained statements.

    This class also lets create multiple processes without creating a class for each process.
    However this does not let use with a manager, where identification has to be explicit.

    """

    @staticmethod
    def task(**kwargs):
        # It needs to be implemented even if it will be replaced.
        pass

    def map(self, f):
        self.task = f
        return self

    def start(self, **kwargs): super().start(**kwargs); return self


class ReverseProcessManager(ReverseManagerMixin, ProcessManager):
    """Alias for a reverse process manager with ReverseManagerMixin. """
    pass
