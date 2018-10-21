import sys
from os import environ
from os.path import join, dirname, realpath, abspath
import subprocess

from savannah.core.logging import logger
from savannah.core.interpreter import AbstractBaseCommand as Command


class CreateSettings(Command):
    verbose_name = 'create-settings'
    help = 'Create default settings file with pre-set values. This will replace your current settings file.'

    def __configure__(self):
        pass

    @staticmethod
    def action(path=None):
        stub_file = abspath(join(dirname(realpath(__file__)), '..', 'settings.pyi'))
        # Process is run from current executable to ensure that Savannah is installed
        try:
            out = subprocess.check_output([sys.executable, stub_file], stderr=subprocess.STDOUT)
            CONFIG_PATH = join(path, 'settings.json') if path else join(environ['SAVANNAH_BASEDIR'], 'settings.json')
            # We can't use settings import to load the config path at this point
            # since we are trying to create the settings.
            # An import fix could enable config path loading even if settings.json does not exist
            # However, this could have repercussions in the way the rest of the modules
            # are used (expecting that settings are configured when they are not),
            # for this reason it is wiser to just define the variable at this scope.

            with open(CONFIG_PATH, "wb") as file:
                file.write(out)

            logger.info("Settings have been created at {}".format(CONFIG_PATH))

        except subprocess.CalledProcessError as err:
            logger.error("Could not create settings. Creation file returned error code {0} and message: \n {1}"
                         .format(err.returncode, err.output))
            sys.exit(err.returncode)

