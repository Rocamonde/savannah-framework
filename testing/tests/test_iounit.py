import pytest
from savannah.iounit import CPUClient
from savannah.iounit.sockets import ConnStatus
from savannah.core.app import App
from os.path import realpath, join, abspath
from os import getcwd

def test_receive_updates():
    # Start server
    app = App(savannah_basedir=abspath(join(realpath(getcwd()), '..', '..', 'test-project')), serverhost=('127.0.0.1', 8000))
    app.start()

    # Start client
    c = CPUClient('127.0.0.1', 8000)
    result = c.message('updates')

    app.stop()
    assert result[0] == ConnStatus.CONN_OK



test_receive_updates()


