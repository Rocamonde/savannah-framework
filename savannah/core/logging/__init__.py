from savannah.core.exceptions import UndefinedEnvironment
logger = None
try:
    from .logging import logger
    logger = logger.logger
except UndefinedEnvironment:
    from .logging import empty_logger as logger
