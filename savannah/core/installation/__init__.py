#
# Installation procedure:
# 1. Create empty folder structure
# 2. Copy blanks files where appropriate
# 3. Run settings creation
#

from os import environ
from os.path import dirname, join, realpath, abspath
import sys
import traceback

from .interpreter import InstallationInterpreter


def execute_from_command_line(argv):
    # Version verifier
    if not (sys.version_info[0] == 3 and sys.version_info[1] >= 6):
        raise RuntimeError("This script requires Python version 3.6 or greater")

    environ['SAVANNAH_INSTALLATION_BASEDIR'] = realpath(dirname(argv[0]))
    environ['SAVANNAH_FRAMEWORK_DIR'] = abspath(join(dirname(realpath(__file__)), '..', '..'))

    interpreter = InstallationInterpreter()

    try:
        interpreter.run(argv[1:])
    except Exception as exc:
        traceback.print_exc()
        sys.exit(1)