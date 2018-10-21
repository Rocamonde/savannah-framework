from savannah.core.interpreter import AbstractBaseCommand as Command


from savannah.core.app import App

#
# TODO: add types to the argument parsing to facilitate data processing and separate it from the logic
#

class Run(Command):
    verbose_name = 'run'
    help = "Run Savannah with configuration from settings.json"

    def __configure__(self):

        self.parser.add_argument('-sh', '--serverhost', nargs='?', type=_types_host,
                                 help='CPUServer host. Either \'<host>\' or \'<host>:<port>\'.')

        self.parser.add_argument('-sp', '--serverport', nargs='?', help='CPUServer port.', type=_types_port)

        self.parser.add_argument('--uihost', nargs='?', type=_types_host,
                                 help='User Interface host. Either \'<host>\' or \'<host>:<port>\'. '
                                      'localui must be enabled in settings.')

        self.parser.add_argument('--uiport', nargs='?', type=_types_port, help='User Interface port.')

        self.parser.add_argument('-l', '--logmode', nargs='?',
                                 help=('Indicate log mode. \'brief\' and \'detailed\' save to log files.'
                                       'Log path must be configured in settings. '),
                                 choices=['console', 'brief', 'detailed'])

    @staticmethod
    def action(serverhost: tuple = None, serverport: int = None, uihost: tuple = None, uiport: int= None, logmode=None):
        app = App()
        app.start()