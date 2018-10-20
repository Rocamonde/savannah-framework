from os.path import join, exists, isdir
from os import listdir
import subprocess
from sys import stderr, stdout

from savannah.core.interpreter import AbstractBaseCommand as Command
from savannah.core import get_basedir


class Test(Command):
    verbose_name = 'test'
    help = "Run tests in development mode."

    def __configure__(self):
        self.parser.add_argument('-o', '--output', default='sys', nargs='?',
                                 help="Specify output for test results. "
                                      "Default is 'sys' and prints to the console. "
                                      "File path absolute or relative from exec path. ")

        self.parser.add_argument('file_or_path', nargs='?',
                                 help="Specify relative or absolute path to file. "
                                      "Relative path is from execution path. ")

    @staticmethod
    def action(file_or_path: str, output: str):
        if file_or_path is None: raise TypeError("Test file name cannot be NoneType")
        usys = True if output is 'sys' else False

        if not exists(file_or_path):
            file_or_path = join(get_basedir(), file_or_path)

        def run_file(f):
            result = subprocess.run(["python", f], **{
                'stdout': stdout if usys else subprocess.STDOUT,
                'stderr': stderr if usys else subprocess.STDOUT
            })

            if not usys:
                with open(output, "a") as output_file:
                    output_file.write(result.stdout)

        if isdir(file_or_path):
            for file in listdir(file_or_path):
                run_file(join(file_or_path, file))
        else:
            run_file(file_or_path)



