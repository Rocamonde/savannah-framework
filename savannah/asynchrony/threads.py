import threading
from queue import Queue

from .base import *

__all__ = ["Thread", "ThreadedLoop", "ThreadManager"]

"""
Threads: same-process asynchronous memory-sharing tasks.
"""


class Thread(AsyncWrapper):

    def __init__(self, name: str, manager: 'ThreadManager' = None, is_daemon: bool = True, has_inbox: bool = True):
        super().__init__(name=name, is_daemon=is_daemon)
        self.manager: ThreadManager = None
        self.__thread: threading.Thread = None

        if has_inbox:
            self.comm_queue = Queue()
        if manager:
            self.implement_manager(manager)

    def start(self, **kwargs) -> None:
        target = self.task if not isinstance(self, LoopMixin) else getattr(self, '_thread_target')
        self.__thread = threading.Thread(target=target,
                                         kwargs=kwargs,
                                         name=self.name)

        self.__thread.daemon = self.is_daemon  # Daemonize thread
        self.__thread.start()  # Start the execution

    def message(self, content, receiver_name: str) -> None:
        """
        .communicate wrapper to ease out communication when receiver_name is known
        """
        m = InboxMessage(content=content,
                         sender=self,
                         receiver=self.manager.find_by_name(receiver_name))
        self.manager.communicate(m)

    def wait(self):
        self.thread.join()

    @property
    def thread(self) -> threading.Thread:
        return self.__thread

    @property
    def is_running(self) -> bool:
        return self.__thread.isAlive() if self.__thread else False


class ThreadedLoop(LoopMixin, Thread):
    """Alias for Thread and LoopMixin. The Mixin takes care of passing all kwargs to Thread."""
    pass


class ThreadManager(Manager):

    def find_by_thread(self, thread: threading.Thread) -> Thread:
        try:
            return self.find_by_name(thread.getName())
        except AttributeError:
            raise WrapperTypeError

    def communicate(self, message: 'InboxMessage'):
        """
        This method permits receiving InboxMessage's form a thread and placing it in the inbox queue of the receiver.
        Each thread has a queue, and these are accessible from anywhere and updated inplace.
        """

        if not isinstance(message, InboxMessage):
            # Not creating another custom error, I consider it excessive.
            raise TypeError("Message is not an instance of QueueMessage")

        self.find_by_name(message.receiver.name).comm_queue.put(message)
