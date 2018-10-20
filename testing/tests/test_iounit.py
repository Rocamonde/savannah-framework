import pytest
from savannah.iounit import CPUClient
from savannah.iounit.sockets import ConnStatus
from savannah.core.management import App
from os.path import realpath, join, dirname


def test_receive_updates():
    # Start server
    app = App()
    app.start(savannah_basedir=join(dirname(realpath(__file__)), '../env/'), serverhost='127.0.0.1', uihost='127.0.0.1', logmode='console')

    # Start client
    c = CPUClient('127.0.0.1', 5555)
    result = c.message('updates')
    print(result)
    assert result[0] == ConnStatus.CONN_OK


test_receive_updates()

