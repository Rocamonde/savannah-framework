import unittest
from savannah.asynchrony import processes
from savannah.asynchrony.pipes import PipeWrapper
from multiprocessing.managers import Namespace
import time
import random


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


class ProcessTest(unittest.TestCase):
    def test_processes_are_unique(self):
        manager = processes.ReverseProcessManager()
        self.assertRaises(processes.WrapperNameError,
                          lambda: manager.propagate([EmptyTestProcess(), EmptyTestProcess()]))

    def test_wait_timeout(self):

        self.assertIs(processes.EasyProcess()
                      .map(lambda: time.sleep(3))
                      .start()
                      .wait(1),     False)

        self.assertIs(processes.EasyProcess()
                      .map(lambda: time.sleep(0))
                      .start()
                      .wait(),     True)

    def test_namespace_and_args(self):
        m = processes.ProcessManager()
        p = NamespaceTestProcess(manager=m)
        m.enable_ioserver()
        m.namespace.data = "hello"
        p.start(arg1="arg2")
        self.assertIs(p.wait(), True)

    def test_pipes(self):
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

        self.assertIs(all((sender.wait(timeout=2), receiver.wait(timeout=2))), True)
        self.assertEqual(*[msg for msg in manager.namespace.msg.values()])

    def test_environ(self):
        import os
        os.environ["var"] = "This is a var"
        p = EnvironProcess()
        p.start()



#
# Main
#


if __name__ == '__main__':
    unittest.main()



