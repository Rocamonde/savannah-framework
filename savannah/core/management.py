import argparse
import sys
from os import environ
from os.path import join, dirname, realpath
import subprocess
from dataclasses import dataclass
import ipaddress

from savannah.core.interpreter import BaseInterpreter
from savannah.core.exceptions import MisconfiguredSettings


# TODO: print result of command-line calls.

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


class CLInterpreter(BaseInterpreter):

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[1:]
        super().__init__(prog='python manage.py')

    def __configure__(self):
        self.stdparser.add_argument('command', nargs='+')

    def execute(self, namespace: argparse.Namespace):
        commands = namespace.__dict__.get('command')
        subparser: BaseInterpreter = mapped_commands[commands[0]](commands[1:])
        subparser.run()


#
# Define commands
#

class Command(BaseInterpreter):
    def __init__(self, argv):
        self.argv = argv
        super().__init__()

class Run(Command):
    def __configure__(self):
        self.stdparser.add_argument('-sh', '--serverhost', nargs='?')
        self.stdparser.add_argument('-sp', '--serverport', nargs='?')
        self.stdparser.add_argument('--uihost', nargs='?')
        self.stdparser.add_argument('--uiport', nargs='?')

    def execute(self, namespace: argparse.Namespace):
        self.start_savannah(**namespace.__dict__)

    @staticmethod
    def start_savannah(serverhost: str = None, serverport=None, uihost=None, uiport=None):
        from savannah.core import settings
        from savannah.core.units import IOUnit, LocalUIUnit, AuthUnit, UploaderUnit

        # Address fetching
        try:
            settings_addr = {}
            settings_addr['iounit'] = _get_split_pair(serverhost, serverport) if serverhost else \
                (settings.workflow.server.address.host, int(settings.workflow.server.address.port))

            if settings.workflow.localui.enabled:
                settings_addr['localui'] = _get_split_pair(uihost, uiport) if uihost else \
                    (settings.workflow.localui.address.host, int(settings.workflow.localui.address.port))

            validated_settings_addr = _validate_addr(settings_addr)

        except TypeError:
            raise MisconfiguredSettings("Invalid data types in settings.json")
        except AttributeError:
            raise MisconfiguredSettings("Missing required configuration properties.")


        # Initialize IOUnit
        iounit = IOUnit(*validated_settings_addr['iounit'])
        iounit.init()

        # Initialize LocalUI
        # TODO: in production, environments with LocalUI should perform a preload
        # TODO  ...to wait while the program loads
        if settings.workflow.localui.enabled:
            localui = LocalUIUnit()
            localui.init()

        # Initialize live upload
        # TODO: for the environments that produce upload upon-request,
        # TODO  ...a different approach must be taken
        if settings.workflow.live_upload:
            uploader_unit = UploaderUnit()
            uploader_unit.init() # TODO: this does not resolve, make init a valid method


class CreateSettings(Command):
    def __configure__(self):
        pass

    def execute(self, namespace: argparse.Namespace):
        self.do_create_settings()

    @staticmethod
    def do_create_settings():
        stub_file = join(dirname(realpath(__file__)), 'settings.pyi')
        # Process is run from current executable to ensure that Savannah is installed
        p = subprocess.Popen([sys.executable, stub_file], stdout=subprocess.PIPE, bufsize=1)
        out = p.stdout.read()

        with open(join(environ['SAVANNAH_BASEDIR'], 'settings.json'), "wb") as file:
            file.write(out)


@dataclass
class Commands:
    run = Run
    create_settings = CreateSettings

cmd = Commands  # alias
mapped_commands = {
            'run': cmd.run,
            'create-settings': cmd.create_settings,
        }


#
# Utils
#


def _get_split_pair(host: str, port: str = None):
    try:
        return host.split(':')[0], int(host.split(':')[1])
    except IndexError:
        return host, int(port)

def _validate_addr(d: dict):
    _d = {}
    for k,v in d.items():
        _d[k] = (_validate_ip(v[0]), v[1])
    return _d

def _validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError as exc:
        if ip == 'local': return '127.0.0.1'
        if ip == 'remote': raise ValueError("Python cannot fetch your machine's IP readily. "
                                            "Please specify the explicit IP for the machine.") from exc