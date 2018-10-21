from savannah.core.management import CLInterpreter
from .actions import *


class InstallationInterpreter(CLInterpreter):

    def __init__(self):
        super().__init__(prog="savannah")

    def __map__(self):
        self.mapped_commands.update({
            'init': Init,
        })

    def __configure__(self):
        from savannah import __version__, __name__

        self.parser.add_argument('-v', '--version', action='version',
                                    version='%(prog)s agent for {n} {v}'.format(v=__version__, n=__name__),
                                    help="Show program's version number and exit.")

        subparsers = self.parser.add_subparsers(help='Command to be executed by the manager.')
        # The following line binds all the command classes as subparsers
        for command_class in self.mapped_commands.values(): command_class(subparsers)

