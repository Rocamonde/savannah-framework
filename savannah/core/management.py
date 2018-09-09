# File to include function to run code, to edit settings file, and so much more
import argparse
import sys
from os import environ
from os.path import join, dirname, realpath
import subprocess
from enum import Enum

from savannah.extensions.interpreter import BaseInterpreter
from savannah.core.exceptions import MisconfiguredSettings

#
# Recognise commands
#

def execute_from_command_line(argv):
    # Version verifier
    if not (sys.version_info[0] == 3 and sys.version_info[1] >= 6):
        raise RuntimeError("This script requires Python version 3.6 or greater")

    environ['SAVANNAH_BASEDIR'] = dirname(argv[0])

    interpreter = CLInterpreter(argv[1:])
    interpreter.run()


class cmd(Enum):
    class Run(BaseInterpreter):
        def __configure__(self):
            self.stdparser.add_argument('-sp', '--serverport', nargs='?')
            self.stdparser.add_argument('-sh', '--serverhost', nargs='?')
            self.stdparser.add_argument('--uiport', nargs='?')
            self.stdparser.add_argument('--uihost', nargs='?')

        def execute(self, namespace: argparse.Namespace):
            self.do_run(**namespace.__dict__)

        def do_run(self, **kwargs):
            start_savannah(**kwargs)

    class CreateSettings(BaseInterpreter):
        def __configure__(self):
            pass

        def execute(self, namespace: argparse.Namespace):
            self.do_create_settings()

        @staticmethod
        def do_create_settings():
            stub_file = join(dirname(realpath(__file__)), 'settings.pyi')
            p = subprocess.Popen(['python', stub_file], stdout=subprocess.PIPE, bufsize=1)
            out = p.stdout.read()

            with open(join(environ['SAVANNAH_BASEDIR'], 'settings.json'), "wb") as file:
                file.write(out)

mapped_commands = {
            'run': cmd.Run,
            'create-settings': cmd.CreateSettings,
        }


class CLInterpreter(BaseInterpreter):

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[1:]
        super().__init__(prog='python manage.py')

    def __configure__(self):
        self.stdparser.add_argument('command', nargs='+')

    def execute(self, namespace: argparse.Namespace):
        commands = namespace.__getattr__('command')
        mapped_commands[commands[0]].value()


#
# Start savannah
#

def get_split_pair(host: str, port: str = None):
    try:
        return host.split(':')[0], int(host.split(':')[1])
    except IndexError:
        return host, int(port)

def start_savannah(serverhost: str = None, serverport=None, uihost=None, uiport=None):
    from savannah.core import settings
    from savannah.core.units import IOUnit

    # Address fetching
    try:
        _iounitaddr = (settings.workflow.server.address.host, int(settings.workflow.server.address.port))
        _uiaddr = (settings.workflow.localui.address.host, int(settings.workflow.localui.address.port))
    except TypeError:
        raise MisconfiguredSettings("Invalid data types in settings.json")

    iounitaddr = get_split_pair(serverhost, serverport) if serverhost else _iounitaddr
    uiaddr = get_split_pair(uihost, uiport) if uihost else _uiaddr


    # Initialize IOUnit
    iounit = IOUnit(*iounitaddr)
    iounit.init()

    # Initialize

    if settings.workflow.localui.enabled:
        pass