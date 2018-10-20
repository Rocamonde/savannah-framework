import logging
import traceback
import os

from .colours import *

__all__ = [
    "produce_trace", "Logger", "logger", "empty_logger"
]


def produce_trace():
    n = 12
    # TODO: improve this implementation
    # This limiter strips the nth last elements to remove the part of generating the log
    # 12 has been set experimentally but depends on how the code is called
    # A better way to stop the traceback could be extending the log class, adding an extra argument
    # to pass with the message (or maybe with a Filter) and producing the trace just before generating the log,
    # So always only the last element would need being removed
    return ['*Traceback* (most recent call last):\n', *traceback.format_stack()][:-n]


#
# Custom format styles and formatters
#

class BaseFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='{', styler=logging.StrFormatStyle):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._style = styler(fmt)

# Stylers
#

class BriefStyler(logging.StrFormatStyle):
    def format(self, record):
        _record = dict(record.__dict__)
        _record['pathname'] = os.path.relpath(os.path.abspath(_record['pathname']), os.environ.get('BASEDIR', ''))
        return self._fmt.format(**_record)

class ConsoleStyler(BriefStyler):
    def format(self, record):
        colour = {
            'WARNING': 'YELLOW',
            'ERROR': 'RED',
            'CRITICAL': 'MAGENTA',
            'INFO': 'BLUE',
            'DEBUG': 'CYAN'
        }[record.__dict__['levelname']]
        return std_bold(colour, super().format(record))

class DetailedStyler(logging.StrFormatStyle):
    def format(self, record):
        _record = dict(record.__dict__)
        _record['pathname'] = os.path.relpath(os.path.abspath(_record['pathname']),
                                              os.environ.get('BASEDIR', ''))
        _record['traceback'] = ''.join(produce_trace())
        return self._fmt.format(**_record)


BriefFormatter = BaseFormatter(
    fmt='| {pathname:<40} | {asctime} | {lineno:>05d} | {funcName:^14} | {levelname:>10}: {message}',
    datefmt='%Y/%m/%d %H:%M:%S',
    styler=BriefStyler)

ConsoleFormatter = BaseFormatter(
    fmt='* {filename}: [{levelname:^8}] |  {message}',
    datefmt='%Y/%m/%d %H:%M:%S',
    styler=BriefStyler)


_fmt = ('#  @ {asctime}, line {lineno:>05d} in {funcName}, \n'
       '*  File path: "{pathname}", \n'
       '*  Process: {processName}, Thread: {threadName} \n'
       '$  {levelname:<10}: {message} \n\n'
       '{traceback}')
_fmt = '*.' * 60 + '\n' + _fmt + '*.' * 60 + '\n\n\n'
DetailedFormatter = BaseFormatter(
    fmt=_fmt, datefmt='%Y/%m/%d %H:%M:%S', styler=DetailedStyler)




#
# Logger class
#

class Logger:
    def __init__(self, name, reload: bool = False, brief_log_file: str = None, detailed_log_file: str = None,
                 do_console: bool = None, do_brief: bool = None, do_detailed: bool = None):
        self.name = name
        do_console = do_console or os.environ.get('LOG_DO_CONSOLE', True)
        do_brief = do_brief or os.environ.get('LOG_DO_BRIEF', False)
        do_detailed = do_detailed or os.environ.get('LOG_DO_DETAILED', False)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.logger.handlers = []  # This is needed for a re-load

        if do_brief:
            self.brief_path = self.check_path('brief', brief_log_file)
            self.add_brief_handler(self.brief_path)

        if do_detailed: self.add_detailed_handler(self.check_path('detailed', detailed_log_file))
        if do_console: self.add_console_handler()

        if reload or not bool(int(os.environ.get('LOG_SESSION_STARTED', '0'))):
            os.environ['LOG_SESSION_STARTED'] = '1'
            if do_brief or do_detailed:
                with open(self.brief_path, "a") as target, \
                        open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "briefheader.txt"),
                             "r") as template:
                    target.write(template.read())

    #
    # Handlers

    def add_brief_handler(self, file):
        # create file handler which logs even debug messages
        fh = logging.FileHandler(file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(BriefFormatter)
        self.logger.addHandler(fh)

    def add_detailed_handler(self, file):
        # file handler that includes detailed traceback
        dfh = logging.FileHandler(file)
        dfh.setLevel(logging.WARNING)
        dfh.setFormatter(DetailedFormatter)
        self.logger.addHandler(dfh)

    def add_console_handler(self):
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(ConsoleFormatter)
        self.logger.addHandler(ch)

    def reload(self): self.__init__(self.name, reload=True)

    #
    # Path validity checker
    @staticmethod
    def check_path(_type, fallback_path):
        _is = False
        from savannah.core.exceptions import UndefinedEnvironment, MisconfiguredSettings

        try:
            from savannah.core import settings
            _path = os.path.join(settings.BASEDIR, settings.log._asdict().get(_type)._asdict().get("path"), '{}.log'.format(_type))
            _is = True
        except UndefinedEnvironment:
                if not fallback_path:
                    raise TypeError("Savannah's environment is undefined. Logfile paths must be specified.")
                else:
                    _path = fallback_path
        except AttributeError:
            raise MisconfiguredSettings(MisconfiguredSettings.missing)
        if not os.path.exists(os.path.dirname(_path)):
            raise (IOError("File's directory does not exist.") if not _is
                   else MisconfiguredSettings(MisconfiguredSettings.invalid_path))
        return _path


logger = Logger(__name__)
empty_logger = logging.getLogger(__name__)
