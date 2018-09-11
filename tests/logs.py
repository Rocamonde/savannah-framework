import unittest
import os
#os.environ["SAVANNAH_BASEDIR"] = "C:\\Users\\pc\\PycharmProjects\\savannah\\"
from savannah.core.logging import Logger

class Logging(unittest.TestCase):
    def test_logger(self):
        l = Logger(__name__)
        l.logger.warning("Message that is warning me of a danger")
