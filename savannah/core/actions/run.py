from os import environ
import ipaddress

from savannah.core.exceptions import MisconfiguredSettings
from savannah.core.logging.logging import logger as _logger
from savannah.core.interpreter import AbstractBaseCommand as Command

#
# TODO: add types to the argument parsing to facilitate data processing and separate it from the logic
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

        assert isinstance(serverhost, str)

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

        # After this we need to reload the logger,
        # since we have changed environment variables that are used
        # when it is first imported.
        _logger.reload()

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
        # if settings.workflow.localui.enabled:
        #    localui = LocalUIUnit()
        #    localui.init()

        # Initialize live upload
        # TODO: for the environments that produce upload upon-request,
        # TODO  ...a different approach must be taken
        # if settings.workflow.live_upload:
        #    uploader_unit = UploaderUnit()
        #    uploader_unit.init() # TODO: this does not resolve, make init a valid method



#
# Utils
#


def _get_split_pair(host: str, port: str = None):
    try:
        return host.split(':')[0], int(host.split(':')[1])
    except IndexError:
        try:
            return host, int(port)
        except TypeError:
            return None

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