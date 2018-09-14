import unittest
import os
from savannah.core.logging import logger

class Logging(unittest.TestCase):
    def test_logger(self):
        logger.warning("Message that is warning me of a danger")
