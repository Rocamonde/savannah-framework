import sys
from os import environ
from os.path import join, dirname, realpath
from abc import abstractmethod
import subprocess
import argparse
import ipaddress

from savannah.core.exceptions import MisconfiguredSettings
from savannah.core.logging import logger
from savannah.core.interpreter import AbstractBaseCommand as Command


#
# Define commands
#

class Run(Command):
    verbose_name = 'run'
    help = "Run Savannah with configuration from settings.json"

    def __configure__(self):

        self.parser.add_argument('-sh', '--serverhost', nargs='?',
                                 help='CPUServer host. Either \'<host>\' or \'<host>:<port>\'.')

        self.parser.add_argument('-sp', '--serverport', nargs='?', help='CPUServer port.')

        self.parser.add_argument('--uihost', nargs='?',
                                 help='User Interface host. Either \'<host>\' or \'<host>:<port>\'. '
                                      'localui must be enabled in settings.')

        self.parser.add_argument('--uiport', nargs='?', help='User Interface port.')

        self.parser.add_argument('-l', '--logmode', nargs='?',
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
        # TODO: if only host is specified, port does not fall back to settings and causes int(NoneType) TypeError
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
        # if settings.workflow.localui.enabled:
        #    localui = LocalUIUnit()
        #    localui.init()

        # Initialize live upload
        # TODO: for the environments that produce upload upon-request,
        # TODO  ...a different approach must be taken
        # if settings.workflow.live_upload:
        #    uploader_unit = UploaderUnit()
        #    uploader_unit.init() # TODO: this does not resolve, make init a valid method


class CreateSettings(Command):
    verbose_name = 'create-settings'
    help = 'Create default settings file with pre-set values. This will replace your current settings file.'

    def __configure__(self):
        pass

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