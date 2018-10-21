import argparse
import sys
from os import environ
from os.path import dirname
import traceback
from typing import Mapping, Iterable

from savannah.core.interpreter import AbstractBaseInterpreter
from savannah.core import actions

#
# Recognise commands
#


def execute_from_command_line(argv):
    # Version verifier
    if not (sys.version_info[0] == 3 and sys.version_info[1] >= 6):
        raise RuntimeError("This script requires Python version 3.6 or greater")

    environ['SAVANNAH_BASEDIR'] = dirname(argv[0])

    interpreter = CLInterpreter()
    try:
        interpreter.run(argv[1:])
    except Exception as exc:
        traceback.print_exc()
        sys.exit(1)


class CLInterpreter(AbstractBaseInterpreter):

    def __init__(self, *args, **kwargs):
        if args or kwargs: super().__init__(*args, **kwargs)
        else: super().__init__(prog='manage.py')

    def __map__(self):
        self.mapped_commands.update({
            'run': actions.run.Run,
            'create-settings': actions.create_settings.CreateSettings,
            'test': actions.test.Test
        })

    def __configure__(self):
        from savannah import __version__, __name__

        self.parser.add_argument('-v', '--version', action='version',
                                    version='%(prog)s agent for {n} {v}'.format(v=__version__, n=__name__),
                                    help="Show program's version number and exit.")

        subparsers = self.parser.add_subparsers(help='Command to be executed by the manager.')
        # The following line binds all the command classes as subparsers
        for command_class in self.mapped_commands.values(): command_class(subparsers)

    def __parse__(self, content: Iterable, *args, **kwargs) -> argparse.Namespace:
        # content[0] contains the command name, content[1:] contains the command arguments
        if len(content) < 1:
            self.parser.print_help(sys.stderr)
            sys.exit(1)

        result = self.parser.parse_args(content)
        result.__setattr__('command_name', content[0])
        return result

    def __interpret__(self, namespace: argparse.Namespace):
        command_name = namespace.command_name
        command_arguments = namespace.__dict__; command_arguments.pop('command_name')
        return command_name, command_arguments

    def __execute__(self, method_name: str, kwargs: Mapping):
        return self.mapped_commands[method_name].action(**kwargs)



class App:
    def start(self, savannah_basedir, *args, **kwargs):
        from savannah.core.actions.run import Run
        environ['SAVANNAH_BASEDIR'] = savannah_basedir
        Run.action(*args, **kwargs)
