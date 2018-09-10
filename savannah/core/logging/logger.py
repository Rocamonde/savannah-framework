import logging
import traceback

def produce_trace():
    n = 12

    # This limiter strips the nth last elements to remove the part of generating the log
    # A better way to stop the traceback could be extending the log class, adding an extra argument
    # to pass with the message (or maybe with a Filter) and producing the trace just before generating the log,
    # So always only the last element would need being removed
    return ['*Traceback* (most recent call last):\n', *traceback.format_stack()][:-n]

class DetailedFormatStyle(logging.StrFormatStyle):
    def format(self, record):
        record.__dict__['levelname'] = '[{}]'.format(record.__dict__['levelname'])
        record.__dict__['traceback'] = ''.join(produce_trace())
        return self._fmt.format(**record.__dict__)

class Formatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='{'):
        fmt = fmt or '* (File: {pathname:<70} @ {asctime}), line {lineno:>05d} in func {funcName:^15} {levelname:>15}: {message}'
        datefmt = datefmt or '%Y/%m/%d %H:%M:%S'
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

class DetailedFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='{', style_class: logging.StrFormatStyle = None):

        fmt = fmt or ('#  (File "{filename:^15}" @ {asctime}, line {lineno:>05d} in {funcName:>15}), \n'
                      '*  File path: "{pathname:<40}", Process: {processName}, Thread {threadName} \n'
                      '{levelname:<15}: {message} \n\n'
                      '{traceback}')
        fmt = '*.'*60 + '\n' + fmt + '*.'*60 + '\n\n\n'
        datefmt = datefmt or '%Y/%m/%d %H:%M:%S'
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._style = DetailedFormatStyle(fmt)


def do_log(brief_log_file, detailed_log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(brief_log_file)
    fh.setLevel(logging.DEBUG)
    # file handler that includes detailed traceback
    dfh = logging.FileHandler(detailed_log_file)
    dfh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    # create formatters (brief and detailed) and add them to the handlers
    formatter = Formatter()
    detailed_formatter = DetailedFormatter()
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    dfh.setFormatter(detailed_formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(dfh)
    # retrieve logger
    return logger

l = do_log('spam.log', 'detailed_spam.log')
l.warning('Warning message')
l.critical('Critical message')
l.info('Info message')
l.debug('Debug message')

