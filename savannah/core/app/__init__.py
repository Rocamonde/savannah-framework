from os import environ
import ipaddress
from savannah.core.exceptions import MisconfiguredSettings
from savannah.core.logging.logging import logger as _logger
from savannah.core.app.units import IOUnit

__all__ = ["App", ]


class App:
    def __init__(self,
                 serverhost: tuple = None, serverport: int = None,
                 uihost: tuple = None, uiport: int= None,
                 logmode=None, savannah_basedir: str = None
                 ):

        if savannah_basedir: environ["SAVANNAH_BASEDIR"] = savannah_basedir
        from savannah.core import settings

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
            settings_addr = dict()

            settings_addr['iounit'] = _get_pair(serverhost, serverport) or \
                                      _get_pair(serverhost, serverport,
                                                _types_host(settings.workflow.server.address.host),
                                                _types_port(settings.workflow.server.address.port))

            if settings.workflow.localui.enabled:
                settings_addr['localui'] = _get_pair(uihost, uiport) or \
                                           _get_pair(uihost, uiport,
                                                     _types_host(settings.workflow.localui.address.host),
                                                     _types_port(settings.workflow.localui.address.port))

            self.validated_addr = _validate_addr(settings_addr)
            self.logmode = logmode
            self.units = dict()

        except TypeError:
            raise MisconfiguredSettings(MisconfiguredSettings.data_types)
        except AttributeError:
            raise MisconfiguredSettings(MisconfiguredSettings.missing)

    def start(self):
        # Initialize IOUnit
        self.units['iounit'] = IOUnit(*self.validated_addr['iounit'])
        self.units['iounit'].init()


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

    def stop(self):
        for unit in self.units.values():
            # TODO: in the future this requires a more thorough clean-up
            unit.stop()


#
# Utils
#

# Data types validation

def _types_host(host: str) -> tuple:
    try:
        return host.split(':')[0], int(host.split(':')[1])
    except IndexError:
        return (host, )


def _types_port(port: str):
    return int(port)


def _get_pair(host: tuple, port: int, fallback_host: tuple = None, fallback_port: int = None):
    assert(type(host) is tuple or host is None)
    # Custom host replaces default
    if host:
        if len(host) == 2: return host

        if port is not None:
            return (*host, port)

        if fallback_port: return (*host, fallback_port)

    # Could not resolve with host and port, return None if there are no optional arguments
    if not fallback_host or not fallback_port: return None

    # If only port is specified, then it replaces default
    if port:
        return (fallback_host[0], port)

    # If there is no available custom, fallback to default
    if len(fallback_host) == 2: return fallback_host
    return (*host, port)


# IP validation
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