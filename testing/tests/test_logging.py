import pytest
import os
from savannah.core.logging.logging import Logger


base_path = os.path.dirname(os.path.realpath(__file__))
brief_path = os.path.join(base_path, 'brief.log')
detailed_path = os.path.join(base_path, 'detailed.log')

def remove_logs():
    try:
        os.remove(brief_path)
        os.remove(detailed_path)
    except FileNotFoundError:
        pass

def create_logger():
    return Logger(__name__, brief_log_file=brief_path, reload=True,
                    detailed_log_file=detailed_path,
                    do_console=True, do_brief=True, do_detailed=True).logger

def test_send_messages():
    remove_logs()
    logger = create_logger()
    logger.warning("txt")
    logger.error("txt")
    logger.info("txt")

