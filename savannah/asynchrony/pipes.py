#
# pipes functionality
#
# The pipe is an object created independently of the manager
# and it lets read and dump raw bytes on either end.
# If duplex pipe is enabled, then two 'pipes' are created that go in opposite directions.
# Pipe connection references can be passed as arguments into processes.
#


from typing import Tuple
import multiprocessing as mp
import multiprocessing.connection
import networkx as nx


__all__ = [
    "UniquePipeError", "PipeNameError", "PipeNetwork", "PipeWrapper"
]


#
# Exceptions
#

class UniquePipeError(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        msg = msg or 'Pair corresponds to an already existing Pipe edge in a pipe-unique PipeNetwork.'
        super().__init__(msg, *args, **kwargs)

class PipeNameError(NameError):
    def __init__(self, msg=None, *args, **kwargs):
        msg = msg or 'Pair does not correspond to any existing Pipe edge.'
        super().__init__(msg, *args, **kwargs)

class ContentError(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

class PipeNotWritableError(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        msg = 'Pipe is not writable. ' + (msg or '')
        super().__init__(msg, *args, **kwargs)

class PipeNotReadableError(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        msg = 'Pipe is not readable. ' + (msg or '')
        super().__init__(msg, *args, **kwargs)


#
# Classes
#


class PipeNetwork:
    """
    Manages the pipes. Lets create, remove and utilize pipes around a graph network easily.
    """

    # TODO: end pipes, remove connections

    def __init__(self, is_unique: bool = True) -> None:
        """
        Initializes PipeNetwork creating a graph
        """

        self.G = nx.DiGraph()
        self.__is_unique: bool = is_unique

        # TODO: implement if necessary multiple pipes for same edges
        if not is_unique:
            raise NotImplementedError

    def populate_network(self, nodes) -> None:
        """
        Populates the network of the included nodes and of the 'MANAGER' node.
        Node addition does not raise any error if already exists.
        """
        for name in nodes:
            self.G.add_node(name)

        self.G.add_node('MANAGER')

    @staticmethod
    def _create_pipe(duplex=True):
        """
        Returns a pair of mp.connection.Connection objects representing the ends of a pipe.
        Piping joins two nodes in a Manager-Process network. Pipes cannot be fed or read
        at each end simultaneously by different threads/processes.
        If duplex is True (the default) then the pipe is bidirectional.
        If duplex is False then the pipe is unidirectional:
        conn1 can only be used for receiving messages and
        conn2 can only be used for sending messages.
        """
        return mp.Pipe(duplex=duplex)

    def insert_pipe(self, endpoints, duplex=True):
        """
        Inserts a pipe that connects each of the endpoints.
        Endpoints are not reversible if duplex is False.
        See ._create_pipe
        endpoints: (receiver, sender)
        """

        # This is not necessary unless something happens while we add one edge and the other.
        if (
                self.G.has_edge(*endpoints) or self.G.has_edge(*endpoints[::-1])
        ) and self.is_unique:
            raise UniquePipeError

        conns = self._create_pipe(duplex=duplex)
        for _conns, _endpoints in \
                zip((conns, conns[::-1]), (endpoints, endpoints[::-1])):

            self.G.add_edge(*_endpoints, **{'pipe': PipeWrapper(_conns), 'duplex': duplex})

    @property
    def is_unique(self):
        return self.__is_unique

    def has_pipe(self, edge: Tuple[str]):
        return self.G.has_edge(*edge)

    def get_pipes(self, node):
        # edge[1] because edge[0] is the origin (node) and edge[1] is the destiny
        # and we want dict indices to categorise by destiny
        return {edge[1]: self.G.get_edge_data(*edge) for edge in self.G.out_edges(node) if edge}

    def is_duplex(self, edge: Tuple[str]):
        try:
            return self.G.get_edge_data(*edge).get('duplex', False)
        except TypeError:
            raise PipeNameError

    @property
    def manager_pipes(self):
        return self.get_pipes('MANAGER')


CLOSING_FLAG = 'CLOSE_CONN_'
class CloseCall(Exception): pass  # This is not really an error


class PipeWrapper:
    def __init__(self, conns: Tuple[mp.connection.Connection]):
        """
        Initialize the Pipe wrapper. In the order provided,
        first connection is always the one to be operated by the
        wrapper owner, and second connection is the unused end.
        """
        pass

        self.__conns = conns

    def send(self, msg):
        cfw = ("Sending a closing flag is disallowed. To close the connection, "
               "use the appropriate method (.close) to avoid confusion.")

        if not self.writable:
            raise PipeNotWritableError

        if msg != CLOSING_FLAG:
            self.__conns[0].send(obj=msg)
        else:
            raise ContentError(cfw)

    def receive(self):
        if not self.readable:
            raise PipeNotReadableError

        msg = self.__conns[0].recv()
        if msg == CLOSING_FLAG:
            raise CloseCall
        else:
            return msg

    @property
    def conns(self): return self.__conns

    @property
    def readable(self): return self.__conns[0].readable

    @property
    def writable(self): return self.__conns[0].writable

    def __enter__(self) -> 'PipeWrapper':
        """
        Enter the pipe communication
        :return: object assigned to the `as` variable
        """

        # We close the foreign connection to leave no end opened.
        self.__conns[1].close()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the pipe communication:
         1. Send closing flag,
         2. Close both ends.
        Returns True if no exceptions shall be considered.
        """
        #
        # Why it is important to send a closing flag
        #
        # If the receiving end is in a blocking loop with no delay,
        # The span of time between receiving a message and blocking again
        # is very little. In that time must the other end close the
        # connection for the recv command not to block (and exit successfully).
        # However, this rarely happens, and if connection is closed after
        # recv has blocked, it won't ever return.
        # For this reason, before closing an end, we always send a closing
        # flag. The flag reading is implemented in the .receive method.

        if exc_type is not CloseCall:
            # If we have received a closing flag,
            # then the connection will already be closed;
            # there is no need in sending a close flag.
            # If not, we send the closing flag for the
            # reciprocal to close too.
            self.__conns[0].send(CLOSING_FLAG)

        self.__conns[0].close()

        if exc_type is CloseCall:
            # Do not raise the exception
            return True

    def close(self, exc_type=None, exc_val=None, exc_tb=None):
        self.__exit__(exc_type, exc_val, exc_tb)
