import argparse
import sys
from os import environ
from os.path import join, dirname, realpath
import subprocess
from dataclasses import dataclass
import ipaddress
from typing import Mapping, Iterable

from savannah.core.interpreter import AbstractBaseInterpreter
from savannah.core.exceptions import MisconfiguredSettings
from savannah.core.logging import logger

#
# Recognise commands
#


def execute_from_command_line(argv):
    # Version verifier
    if not (sys.version_info[0] == 3 and sys.version_info[1] >= 6):
        raise RuntimeError("This script requires Python version 3.6 or greater")

    environ['SAVANNAH_BASEDIR'] = dirname(argv[0])

    interpreter = CLInterpreter()
    interpreter.run(argv[1:])


class CLInterpreter(AbstractBaseInterpreter):

    def __init__(self, argv=None):
        super().__init__(prog='manage.py')

    def __configure__(self):
        from savannah import __version__, __name__

        self.parser.add_argument('-v', '--version', action='version',
                                    version='%(prog)s agent for {n} {v}'.format(v=__version__, n=__name__),
                                    help="Show program's version number and exit.")

        subparser = self.parser.add_subparsers() # title, description, help
        # Configure here rest of subparsers
    def __parse__(self, content: Iterable, *args, **kwargs) -> argparse.Namespace:
        pass

    def __interpret__(self, namespace: argparse.Namespace):
        pass

    def __execute__(self, method_name: str, kwargs: Mapping):
        pass


#
# Define commands
#

class Run(Command):
    def __configure__(self):

        self.stdparser.add_argument('-sh', '--serverhost', nargs='?',
                                    help='CPUServer host. Either \'<host>\' or \'<host>:<port>\'.')

        self.stdparser.add_argument('-sp', '--serverport', nargs='?', help='CPUServer port.')

        self.stdparser.add_argument('--uihost', nargs='?',
                                    help='User Interface host. Either \'<host>\' or \'<host>:<port>\'. '
                                    'localui must be enabled in settings.')

        self.stdparser.add_argument('--uiport', nargs='?', help='User Interface port.')

        self.stdparser.add_argument('-l', '--logmode', nargs='?',
                                    help=('Indicate log mode. \'brief\' and \'detailed\' save to log files.'
                                          'Log path must be configured in settings. '),
                                    choices=['console', 'brief', 'detailed'])


    @staticmethod
    def action(serverhost: str = None, serverport=None, uihost=None, uiport=None, logmode=None):
        from savannah.core import settings
        from savannah.core.units import IOUnit, LocalUIUnit, AuthUnit, UploaderUnit

        #
        # We set the log mode

        if logmode == 'brief':
            environ.update({
                'LOG_DO_BRIEF': '1'
            })
        elif logmode in ('detailed', 'extended'):  # Both terms are sufficiently intuitive for command line
            environ.update({
                'LOG_DO_BRIEF': '1',
                'LOG_DO_DETAILED': '1',
            })

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
            raise MisconfiguredSettings(MisconfiguredSettings.data_types)
        except AttributeError:
            raise MisconfiguredSettings(MisconfiguredSettings.missing)


        # Initialize IOUnit
        iounit = IOUnit(*validated_settings_addr['iounit'])
        iounit.init()

        # Initialize LocalUI
        # TODO: in production, environments with LocalUI should perform a preload
        # TODO  ...to wait while the program loads
        #if settings.workflow.localui.enabled:
        #    localui = LocalUIUnit()
        #    localui.init()

        # Initialize live upload
        # TODO: for the environments that produce upload upon-request,
        # TODO  ...a different approach must be taken
        #if settings.workflow.live_upload:
        #    uploader_unit = UploaderUnit()
        #    uploader_unit.init() # TODO: this does not resolve, make init a valid method


class CreateSettings(Command):

    @staticmethod
    def action():
        stub_file = join(dirname(realpath(__file__)), 'settings.pyi')
        # Process is run from current executable to ensure that Savannah is installed
        p = subprocess.Popen([sys.executable, stub_file], stdout=subprocess.PIPE, bufsize=1)
        out = p.stdout.read()

        CONFIG_PATH = join(environ['SAVANNAH_BASEDIR'], 'settings.json')
        # We can't use settings import to load the config path at this point
        # since we are trying to create the settings.
        # An import fix could enable config path loading even if settings.json does not exist
        # However, this could have repercussions in the way the rest of the modules
        # are used (expecting that settings are configured when they are not),
        # for this reason it is wiser to just define the variable at this scope.

        with open(CONFIG_PATH, "wb") as file:
            file.write(out)

        logger.info("Settings have been created at {}".format(CONFIG_PATH))


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