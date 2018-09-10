import unittest
from savannah.iounit import CPUClient

class SocketConnection(unittest.TestCase):
    def test_receive_updates(self):
        c = CPUClient('127.0.0.1', 5555)
        print(c.message('updates'))