import unittest
from savannah.iounit import CPUClient
from savannah.iounit.sockets import ConnStatus

class SocketConnection(unittest.TestCase):
    def test_receive_updates(self):
        c = CPUClient('127.0.0.1', 5555)
        result = c.message('updates')
        print(result)
        self.assertEqual(result[0], ConnStatus.CONN_OK)