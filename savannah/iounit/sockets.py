#
# Sockets communication.
# Model is thought for client--Rest-server many-to-one connections.
# For P2P communications other models should be used.
#

import socket
from pydoc import locate
import pickle
from typing import *
from enum import Enum

from savannah.asynchrony import threads
from savannah.iounit.interpreter import CPUInterpreter
from savannah.core.interpreter import EvaluationException
from savannah.core.logging import logger

__all__ = ['CPUServer', 'CPUClient', 'Utils', 'ConnStatus']


#
# Custom error messages for communication
#

class ConnectionResponseStatus(Enum):
    """
    Enumeration comprising different integer values
    mapped to different connection statuses.

    Error codes are used to prevent exceptions
    on either side form propagating to the other.
    """
    # This can be easily extended; for now only basic statuses are included.

    CONN_OK             = 100
    CONN_REFUSED        = 200
    CONN_UNKNOWN_ERR    = 300
    SERVER_UNKNOWN_ERR  = 400
    RESPONSE_DATA_ERR   = 500
    KNOWN_ERR           = 600

    CONN_NOT_OK         = (CONN_REFUSED, CONN_UNKNOWN_ERR, SERVER_UNKNOWN_ERR, RESPONSE_DATA_ERR, KNOWN_ERR)

ConnStatus = ConnectionResponseStatus  # Alias


#
# Classes
#

class CPUServer:
    def __init__(self, host, port, interpreter: CPUInterpreter, backlog=4):
        self.__interpreter = interpreter

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.backlog = backlog

        self.curr_addr = self.curr_conn = None
        self.close_flag = False

        self.__thread: threads.Thread = None

        self.socket.bind((self.host, self.port))

    def __listen(self):
        # This call starts to admit incoming connections that are added into a queue.
        # When `.accept` is executed, connections start to be accepted in order of inclusion.
        # Backlog is the maximum number of connections that can await in the queue without
        # having been accepted yet. This call does not block. Socket will listen in another
        # thread. What blocks is accepting a connection (if there are no connections awaiting).

        self.socket.listen(self.backlog)

    class BackgroundLoop(threads.Thread):
        def __init__(self, mother: 'CPUServer'):
            self._mother = mother
            super(CPUServer.BackgroundLoop, self).__init__(name='InternalServerBackgroundLoop',
                                                           is_daemon=False)

        def task(self):
            while not self._mother.close_flag:

                # The following statement blocks when there are no connections in the queue.
                # If the server flag to stop has been changed, to make the loop break we only
                # need to send a connection with some empty message.

                self._mother.curr_conn, self._mother.curr_addr = curr_conn, curr_addr = self._mother.socket.accept()
                logger.info("[CPUServer]: New incoming connection at {addr}".format(addr=curr_addr))
                try:
                    raw_message = Utils.recv_message(curr_conn)

                    # The empty connection to close the thread can contain anything, but using
                    # a conventional word saves up time since the interpreter is not involved.
                    if raw_message and raw_message != b'NEXT':
                        message = raw_message.decode()
                        logger.info("[CPUServer]: {addr} sent: \"{msg}\"".format(addr=curr_addr, msg=message))

                        response = self._mother.interpret_and_execute(message)
                        response_type = type(response)

                        if response_type not in (bytes, str):
                            response = pickle.dumps(response)
                        elif response_type is str:
                            response = response.encode()

                        Utils.send_message(curr_conn, b'exec_ok:1')
                        logger.info("[CPUServer]: {addr} request [EXEC_OK]".format(addr=curr_addr))

                        Utils.send_message(curr_conn, 'data_type:{}'.format(response_type.__name__).encode())
                        Utils.send_message(curr_conn, response)
                        logger.info("[CPUServer]: {addr} request was successfully responded with data_type {dt}"
                                    .format(addr=curr_addr, dt=response_type.__name__))

                except (ConnectionError, OSError) as e:
                    # TODO: This should be carefully tested in the future.
                    # Current tests indicate that this exception is due to a finalised
                    # connection at the other side.
                    logger.warning("[CPUServer]: {addr} [ERROR]: {msg}".format(addr=curr_addr,
                                                                               msg=Utils.exception_message(e)))

                except EvaluationException as e:
                    Utils.send_message(curr_conn, b'exec_ok:0')
                    Utils.send_message(curr_conn, Utils.exception_message(e).encode())
                    logger.warning("[CPUServer]: {addr} [EVALUATION_EXCEPTION]: {msg}"
                                   .format(addr=curr_addr, msg=Utils.exception_message(e)))

                finally:
                    self._mother.curr_conn.close()
                    logger.info("[CPUServer]: {addr} connection closed.".format(addr=curr_addr))
                    del curr_addr, curr_conn

    def run(self):
        self.__listen()
        self.__thread = CPUServer.BackgroundLoop(self)
        self.__thread.start()

    def close(self, timeout=None):
        self.close_flag = True
        # This will set a flag that the loop will check after finalizing the last connection.
        # Most commonly there will be no connections awaiting and the acceptance call will block,
        # so the flag will most likely be changed in this moment.
        # To fix this we send an empty connection.
        self.thread.thread.join(timeout=0.5)
        if self.thread.is_running:
            CPUClient(self.host, self.port).message('NEXT')

        self.thread.thread.join(timeout=timeout)

        # Al terminal el hilo se cierra el socket.
        self.socket.close()

    def interpret_and_execute(self, message: str):
        return self.__interpreter.raw_run(message)

    @property
    def thread(self) -> threads.Thread:
        return self.__thread


class CPUClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket: socket.socket = None

    def message(self, content: str) -> Tuple[ConnStatus, Any]:
        # Cada vez que se envía un mensaje se crea un nuevo socket porque el servidor está configurado para
        # admitir solamente una petición de cada socket.
        # Si fuera necesario mantener al servidor en línea con el cliente, se podría modificar su comportamiento y
        # crear una nueva clase; pedir al principio una confirmación del tipo de petición para dirigir el flujo
        # acorde.

        try:
            self.socket = socket.socket()
            self.socket.connect((self.host, self.port))
            Utils.send_message(self.socket, content.encode())
            exec_message = Utils.recv_message(self.socket)
            if exec_message:
                # Server has responded. We will parse response status:
                status_int = exec_message.decode().split(':')[1]
                if int(status_int):
                    # Server response is satisfactory. We will parse received data.
                    raw_datatype = Utils.recv_message(self.socket)
                    raw_data = Utils.recv_message(self.socket)

                    if locate(raw_datatype.decode().split(':', 1)[1]) is str:
                        data = raw_data.decode()
                    else:
                        data = pickle.loads(raw_data)
                    return ConnStatus.CONN_OK, data
                else:
                    # Server has responded but repsonse is not ok.
                    error_str = Utils.recv_message(self.socket).decode()
                    if error_str:
                        errname, errmsg = error_str.split(':', 1)
                        return ConnStatus.KNOWN_ERR, (errname, errmsg)

            # Server has not responded. Server is down.
            # Statement is not in else clause to provide fallback for nested ifs.
            return ConnStatus.SERVER_UNKNOWN_ERR, None

        except ConnectionRefusedError as e:
            return ConnStatus.CONN_REFUSED, e
        except ConnectionError as e:
            return ConnStatus.CONN_UNKNOWN_ERR, e
        except pickle.UnpicklingError as e:
            return ConnStatus.RESPONSE_DATA_ERR, e


class Utils:
    @staticmethod
    def send_message(socket: socket.socket, message: bytes):
        length = str(len(message)).zfill(8).encode()
        socket.send(length)
        socket.send(message)

    @staticmethod
    def recv_message(socket: socket.socket) ->Union[bytes, None]:
        length = socket.recv(8)
        try:
            return socket.recv(int(length))
        except ValueError:
            return None

    @staticmethod
    def socket_available(host, port):
        from contextlib import closing
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            return sock.connect_ex((host, port))

    @staticmethod
    def exception_message(e):
        return '{err_name}:{msg}'.format(err_name=e.__class__.__name__, msg=e)

