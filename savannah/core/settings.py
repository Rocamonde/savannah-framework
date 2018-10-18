#
# File for dynamically importing constants from settings
#

import os
from savannah.core.extensions.config import Configuration
from savannah.core.exceptions import UndefinedEnvironment
from savannah.core import get_basedir

BASEDIR = get_basedir()

CONFIG_PATH = os.path.join(BASEDIR, 'settings.json')

_config_obj = Configuration(config_path=CONFIG_PATH)

# For the stub to work, we just have to make a first
# reference to the root variables:
workflow = None; enabled_sensors = None; info = None; log = None

globals().update(_config_obj.data._asdict())
