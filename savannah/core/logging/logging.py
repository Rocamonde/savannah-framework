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

class BriefFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='{'):
        #  Brief formatting includes context and file information, but does not include traceback.
        fmt = fmt or '| {pathname:<40} | {asctime} | {lineno:>05d} | {funcName:^14} | {levelname:>10}: {message}'
        datefmt = datefmt or '%Y/%m/%d %H:%M:%S'
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._style = BriefFormatter.Style(fmt)

    class Style(logging.StrFormatStyle):
        def format(self, record):
            _record = dict(record.__dict__)
            _record['pathname'] = os.path.relpath(os.path.abspath(_record['pathname']), os.environ.get('BASEDIR', ''))
            return self._fmt.format(**_record)


class ConsoleFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='{'):
        # Console formatting includes only basic information.
        fmt = fmt or '* {filename}: [{levelname:^8}] |  {message}'
        datefmt = datefmt or '%Y/%m/%d %H:%M:%S'
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._style = ConsoleFormatter.Style(fmt)

    class Style(logging.StrFormatStyle):
        def format(self, record):
            _record = dict(record.__dict__)
            _record['pathname'] = os.path.relpath(os.path.abspath(_record['pathname']), os.environ.get('BASEDIR', ''))
            return self._fmt.format(**_record)


class DetailedFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='{', style_class: logging.StrFormatStyle = None):
        # Detailed formatter includes thread name, process name, traceback. Enabled for warnings or worse
        fmt = fmt or ('#  @ {asctime}, line {lineno:>05d} in {funcName}, \n'
                      '*  File path: "{pathname}", \n'
                      '*  Process: {processName}, Thread: {threadName} \n'
                      '$  {levelname:<10}: {message} \n\n'
                      '{traceback}')
        fmt = '*.'*60 + '\n' + fmt + '*.'*60 + '\n\n\n'
        datefmt = datefmt or '%Y/%m/%d %H:%M:%S'
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._style = DetailedFormatter.Style(fmt)

    class Style(logging.StrFormatStyle):
        def format(self, record):
            _record = dict(record.__dict__)
            _record['pathname'] = os.path.relpath(os.path.abspath(_record['pathname']),
                                                  os.environ.get('BASEDIR', ''))
            _record['levelname'] = '[{}]'.format(_record['levelname'])
            _record['traceback'] = ''.join(produce_trace())
            colour = {
                'WARNING': 'YELLOW',
                'ERROR': 'RED',
                'CRITICAL': 'MAGENTA',
                'INFO': 'BLUE',
                'DEBUG': 'CYAN'
            }[_record['levelname']]

            return std_bold(colour, self._fmt.format(**_record))

#
# Logger class
#

class Logger:
    def __init__(self, name, blf: str = None, dlf: str = None,
                 do_console: bool = None, do_brief: bool = None, do_detailed: bool = None):
        do_console = do_console or os.environ.get('LOG_DO_CONSOLE', True)
        do_brief = do_brief or os.environ.get('LOG_DO_BRIEF', False)
        do_detailed = do_detailed or os.environ.get('LOG_DO_DETAILED', False)

        if do_brief or do_detailed:
            _is = False
            from savannah.core.exceptions import UndefinedEnvironment, MisconfiguredSettings

            try:
                from savannah.core import settings
                global settings
                _is = True
            except UndefinedEnvironment:
                if not blf or not dlf:
                    raise TypeError("Savannah's environment is undefined. Logfile paths must be specified.")
            finally:
                try:
                    # We can do this because if first element evals to True, second is not checked
                    blf = blf or os.path.join(settings.BASEDIR, settings.log.brief.path, 'brief.log')
                    dlf = dlf or os.path.join(settings.BASEDIR, settings.log.detailed.path, 'detailed.log')
                    if not (os.path.exists(os.path.dirname(blf)) and os.path.exists(os.path.dirname(dlf))):
                        raise (IOError("File's directory does not exist.") if _is
                               else MisconfiguredSettings(MisconfiguredSettings.invalid_path))
                except AttributeError:
                    raise MisconfiguredSettings(MisconfiguredSettings.missing)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if do_brief:
            # create file handler which logs even debug messages
            fh = logging.FileHandler(blf)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(BriefFormatter())
            self.logger.addHandler(fh)

        if do_detailed:
            # file handler that includes detailed traceback
            dfh = logging.FileHandler(dlf)
            dfh.setLevel(logging.WARNING)
            dfh.setFormatter(DetailedFormatter())
            self.logger.addHandler(dfh)

        if do_console:
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(ConsoleFormatter())
            self.logger.addHandler(ch)

        if not bool(int(os.environ.get('LOG_SESSION_STARTED', '0'))):
            os.environ['LOG_SESSION_STARTED'] = '1'
            if do_brief or do_detailed:
                with open(blf, "a") as target, \
                        open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "briefheader.txt"),
                             "r") as template:

                    target.write(template.read())


logger = Logger(__name__)
empty_logger = logging.getLogger(__name__)
