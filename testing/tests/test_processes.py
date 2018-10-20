import pytest
from savannah.asynchrony import processes
from savannah.asynchrony.pipes import PipeWrapper
from multiprocessing.managers import Namespace
import time
import random

#
# Process definitions
#

class EmptyTestProcess(processes.Process):
    @staticmethod
    def task(**kwargs):
        pass

class NamespaceTestProcess(processes.Process):
    @staticmethod
    def task(**kwargs):
        print(kwargs)

class EnvironProcess(processes.Process):
    @staticmethod
    def task():
        import os
        print(os.environ.get("var"))

class SenderProcess(processes.Process):
    @staticmethod
    def task(pipe_map: dict, namespace: Namespace):
        with pipe_map.get('ReceiverProcess').get('pipe') as pipe:
            msg = b""
            while namespace.cont:
                i = "{}".format(random.random()).encode()
                msg += i
                pipe.send(i)
                time.sleep(0.4)

            namespace.msg['SenderProcess'] = msg

class ReceiverProcess(processes.Process):
    @staticmethod
    def task(pipe_map: dict, namespace: Namespace):
        pipe: PipeWrapper = pipe_map.get('SenderProcess').get('pipe')
        if pipe.readable:
            with pipe:
                msg = b""
                while namespace.cont:
                    msg += pipe.receive()

        namespace.msg['ReceiverProcess'] = msg


#
# Tests
#

def test_processes_are_unique():
    manager = processes.ReverseProcessManager()
    with pytest.raises(processes.WrapperNameError):
        manager.propagate([EmptyTestProcess(), EmptyTestProcess()])


def test_wait_timeout():
    assert not processes.EasyProcess().map(lambda: time.sleep(3)).start().wait(1)
    assert processes.EasyProcess().map(lambda: time.sleep(0)).start().wait()


def test_namespace_and_args():
    m = processes.ProcessManager()
    p = NamespaceTestProcess(manager=m)
    m.enable_ioserver()
    m.namespace.data = "hello"
    p.start(arg1="arg2")
    assert p.wait()

def test_pipes():
    sender = SenderProcess()
    receiver = ReceiverProcess()
    manager = processes.ReverseProcessManager()
    manager.propagate([sender, receiver])
    manager.pipe_network.insert_pipe((receiver.name, sender.name), duplex=False)
    manager.enable_ioserver()
    manager.namespace.cont = True

    # Dicts have to be created by this method for changes to propagate
    manager.namespace.msg = manager.ioserver.dict(dict())
    manager.start_all()
    time.sleep(3)
    manager.namespace.cont = False

    assert all((sender.wait(timeout=2), receiver.wait(timeout=2)))
    assert len(set([msg for msg in manager.namespace.msg.values()])) <= 1

def test_environ():
    import os
    os.environ["var"] = "This is a var"
    p = EnvironProcess()
    p.start()





