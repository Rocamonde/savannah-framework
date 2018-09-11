import time
from typing import TypeVar, Any, Dict, Iterable, Union
from abc import abstractmethod, ABC

from savannah.core.logging import logger


__all__ = [

    # Classes
    "AsyncWrapper", "LoopMixin", "Manager", "ReverseManagerMixin", "InboxMessage",
    # Errors
    "DeadAsyncObjectError", "WrapperNameError", "ManagerTypeError", "WrapperTypeError"
]


"""
Core exceptions
"""

# TypeError extensions


class WrapperTypeError(TypeError):
    def __init__(self, msg = None, *args, **kwargs):
        msg = msg or 'The Wrapper passed is not an instance of AsyncWrapper or any of its subclasses.'
        super().__init__(
            msg,
            *args, **kwargs
        )


class ManagerTypeError(TypeError):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'The thread cannot be initialized without a proper instance of Manager.',
            *args, **kwargs
        )


class DeadAsyncObjectError(TypeError):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'The Wrapper passed contains a dead async object. \
            Only running objects or objects that have not yet started are accepted.',
            *args, **kwargs
        )


# KeyError Extensions

class WrapperNameError(KeyError):
    # No specific message defined because class does not explicitly indicate why it is wrong, but what is wrong.
    def __init__(self, msg, *args, **kwargs):
        super().__init__(
            msg, *args, **kwargs
        )

    already_exists = 'The name specified for the AsyncWrapper already exists in that Manager.'
    does_not_exist = 'The name specified for the AsyncWrapper does not exist.'


"""
AsyncWrapper: wrapper for asynchronous objects management.
"""


def set_sf_exec(flag: str, value: Any):
    """Sets a flag attribute contained in self to the value specified after execution"""

    def decorator(func):
        def wrapper(self: object, *args, **kwargs):
            func(*args, **kwargs)
            self.__setattr__(flag, value)

        return wrapper

    return decorator


class AsyncWrapper(ABC):

    def __init__(self, **kwargs) -> None:
        self.__started_flag: bool = False

        # Fallback for object name to be lower class' name.
        # To avoid implementation conflicts, a custom name
        # can be specified.
        _nd = self.__class__.__name__
        self.__name: str = kwargs.get('name', _nd) or _nd
        if self.__name.upper() == 'MANAGER':
            raise WrapperNameError("Wrapper cannot be called 'Manager'. "
                                   "Name is reserved.")

        is_daemon = kwargs.get('is_daemon')
        if is_daemon is not None:
            # this explicitly checks if result exists
            self.__is_daemon: bool = is_daemon

    @abstractmethod
    def task(self, **kwargs):
        """Tasks to be done by the async object"""
        pass

    @set_sf_exec('__started_flag', True)
    @abstractmethod
    def start(self, **kwargs):
        """Start the async object"""
        pass

    def implement_manager(self, manager: 'Manager', reverse=False) -> None:
        # Manager implementation is NOT automatic by default.
        # However it is currently in the processes and threads class blueprints
        # as they are at the time (only if a manager is specified).
        # This can be changed at any time, and any specific instance method can
        # easily be decorated with manager implementation.

        if not isinstance(manager, Manager):
            raise ManagerTypeError

        if manager.find_by_name(name=self.name):
            raise WrapperNameError(WrapperNameError.already_exists)

        if self.is_running:
            raise WrapperTypeError("Cannot implement into manager: Wrapper already running.")

        self.manager: 'Manager' = manager

        if not reverse:
            self.manager.add_wrapper(self)

    @abstractmethod
    def wait(self):
        pass

    def fetch_target(self):
        return self.task if not isinstance(self, LoopMixin) else getattr(self, '_loop_target')

    @property
    def name(self) -> str:
        return self.__name

    @property
    @abstractmethod
    def is_running(self):
        """Checks whether async object is running"""
        """CAUTION
        THIS MAY RETURN TRUE IF .join METHOD IS NOT CALLED FOR BOTH THREADS AND PROCESSES"""
        # TODO: Necessary to investigate
        pass

    @property
    def has_begun(self) -> bool:
        return self.__started_flag

    @property
    def is_daemon(self) -> bool:
        try:
            return self.__is_daemon
        except AttributeError as exc:
            raise AttributeError("AsyncWrapper has not been specified an `is_daemon` value.") from exc


_cotype_AsyncWrapper = TypeVar('_cotype_AsyncWrapper', bound=AsyncWrapper, covariant=True)


def _implement_manager(func):
    """ Decorator for implementing the manager as a method inside a class
        Instance needs to have .implement_manager method and
        method being decorated needs to be passed a manager as a kwarg"""
    def wrapper(self: _cotype_AsyncWrapper, *args, **kwargs):
        func(self, *args, **kwargs)
        manager = kwargs.get('manager')
        if manager:
            self.implement_manager(manager=kwargs.get('manager'))
        else:
            raise TypeError("Method takes a 'manager' key word argument to be able to implement the manager.")

    return wrapper


class LoopMixin(AsyncWrapper):
    def __init__(self, interval: float, **kwargs) -> None:
        super().__init__(**kwargs)

        self.__interval: float = interval
        self.__cont: bool = True

    def _loop_target(self, **kwargs):
        while self.__cont:
            self.task(**kwargs)
            time.sleep(self.__interval)

    def stop(self):
        if self.__cont: self.__cont = False
        else:
            logger.warning("Async object has already been stopped.")

    @property
    def continue_flag(self) -> bool:
        return self.__cont


class Manager(ABC):

    def __init__(self) -> None:
        self.__wrappers: Dict[_cotype_AsyncWrapper] = dict()

    @property
    def wrappers_list(self) -> Iterable[_cotype_AsyncWrapper]:
        return self.__wrappers.values()

    @property
    def wrappers_dict(self) -> Dict:
        return self.__wrappers

    def find_by_name(self, name: str) -> _cotype_AsyncWrapper:
        return self.__wrappers.get(name)

    def add_wrapper(self, wrapper: AsyncWrapper, reverse=False, manager: 'Manager' = None):
        """
        Adds a wrapper to the Manager. If reverse is true, it calls Process.implement_manager
        """
        if not isinstance(wrapper, AsyncWrapper):
            raise WrapperTypeError

        if not wrapper.is_running and wrapper.has_begun:
            raise DeadAsyncObjectError

        if reverse:
            wrapper.implement_manager(manager, reverse=reverse)

        self.__wrappers[wrapper.name] = wrapper

    def start_all(self, *args, **kwargs):
        # Only use if strictly explicit
        for wrapper in self.wrappers_list:
            wrapper.start(*args, **kwargs)


class ReverseManagerMixin(Manager):
    """
    This class permits adding wrappers automatically from a list into the manager.
    It is thought to avoid passing a manager instance to each wrapper.
    """
    def propagate(self, reverse_list: Iterable[AsyncWrapper]):
        [self.add_wrapper(wrapper=wrapper, reverse=True, manager=self) for wrapper in reverse_list]


"""
InboxMessage: Private, nested communication object
"""

_type_async_str = Union[_cotype_AsyncWrapper, str]

#
# -- str or _cotype_AsyncWrapper? --
#
# Type will be either AsyncWrapper or str depending on whether it is a Thread or a Process.
# Threads can communicate directly with shared-memory-same-object pointers; processes cannot,
# so passing the process instance would be useless and wasteful since no operation made inplace
# would take effect into the real process, and object would be duplicated.
#


class InboxMessage:

    def __init__(self, content,
                 sender: _type_async_str, receiver: _type_async_str,
                 previous_message: 'InboxMessage' = None):

        if previous_message is not None and not isinstance(previous_message, InboxMessage):
            raise TypeError("Message is not an instance of InboxMessage")

        self.__previous: InboxMessage = previous_message
        self.__content = content
        self.__sender: _type_async_str = sender
        self.__receiver: _type_async_str = receiver

    @property
    def previous(self) -> 'InboxMessage': return self.__previous

    @property
    def content(self): return self.__content

    @property
    def sender(self) -> _type_async_str: return self.__sender

    @property
    @abstractmethod
    def receiver(self) -> _type_async_str: return self.__receiver

    def response(self, content):
        return InboxMessage(content, sender=self.receiver, receiver=self.sender, previous_message=self)
