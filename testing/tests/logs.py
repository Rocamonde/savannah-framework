import unittest
import os
from savannah.core.logging.logging import Logger


class Logging(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.brief_path = os.path.join(self.base_path, 'brief.log')
        self.detailed_path = os.path.join(self.base_path, 'detailed.log')

    def remove_logs(self):
        try:
            os.remove(self.brief_path)
            os.remove(self.detailed_path)
        except FileNotFoundError:
            pass

    def create_logger(self):
        return Logger(__name__, brief_log_file=self.brief_path, reload=True,
                        detailed_log_file=self.detailed_path,
                        do_console=True, do_brief=True, do_detailed=True).logger

    def test_send_messages(self):
        self.remove_logs()
        logger = self.create_logger()
        logger.warning("txt")
        logger.error("txt")
        logger.info("txt")


if __name__ == "__main__":
    unittest.main()
