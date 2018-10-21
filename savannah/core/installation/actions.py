from savannah.core.interpreter import AbstractBaseCommand as Command
import re
import argparse
import os
import sys
import fnmatch
from savannah.core.exceptions import UndefinedEnvironment
import yaml
import datetime

from savannah import __version__ as SAVANNAH_VERSION

def _validProjName(s: str):
    s = s.strip()
    if re.match('^[\w-]+$', s) is None:
        raise argparse.ArgumentTypeError("Project name '{}' is not a valid project name. "
                                         "Alphanumeric characters and hyphens are allowed.".format(s))
    return s


class Init(Command):
    verbose_name = 'init'
    help = "Initialize savannah project in the current folder"

    def __configure__(self):

        self.parser.add_argument('project_name', type=_validProjName,
                                 help='Project name. This will be used to '
                                      'create the folder and the default files')

    @staticmethod
    def action(project_name: str):
        try:
            running_path = os.environ['SAVANNAH_INSTALLATION_BASEDIR']
            savannah_path = os.environ['SAVANNAH_FRAMEWORK_DIR']
        except KeyError as exc:
            raise UndefinedEnvironment("Savannah installation environment variables are undefined. "
                                       "Cannot run installation.") from exc

        proj_folder = os.path.join(running_path, project_name)
        defaults_folder = os.path.join(savannah_path, 'core', 'defaults')

        #
        # We first check if the folder already exists, before going further on

        if os.path.exists(proj_folder):
            print("Path already exists. Please, choose a different name or folder.\n")
            sys.exit(1)

        #
        # Now we get information for the project
        intro_phrase = 'Please specify the following information about your project'
        project_data = {
            'display_name': 'Project display name',
            'project_owner': 'Project owner (person or organisation)',
            'project_owner.email': 'Email',
        }

        print(intro_phrase, "\n")
        for key, val in project_data.items():
            project_data[key] = input(val+': ')

        print("There we go!")

        project_data.update({
            'project_name': project_name,
            'creation_date': datetime.datetime.now().date().strftime('%d/%m/%Y')
        })

        SAVANNAH_PROJECT_INFORMATION = {
            'project_info': project_data,
            'project_type': 'savannah_framework',
            'savannah_version': SAVANNAH_VERSION,
        }

        # Preparing paths
        inf = yaml.load(open(os.path.join(defaults_folder, 'inf.yml')))

        ignore_filter = inf.get("ignore", [])
        ignore_filter = [os.path.join(defaults_folder, i) for i in ignore_filter]
        paths = [os.path.join(dirpath, filename)
                 for dirpath, dirnames, filenames in os.walk(defaults_folder)
                 for filename in filenames]

        ignore = [l for ifilter in ignore_filter for l in fnmatch.filter(paths, ifilter)]
        files = [_ for _ in paths if _ not in ignore]

        # Create base directory
        os.mkdir(proj_folder)

        # Copy files
        for file in files:
            destination = os.path.abspath(os.path.join(proj_folder, os.path.relpath(file, defaults_folder)))
            with open(file, "r") as content, open(destination, "w+") as destfile:
                c = content.read()
                for key, val in project_data.items():
                    c = c.replace('{'+key+'}', val)
                destfile.write(c)
                print("Writing {} ... done".format(file))

        # Create project information file
        with open(os.path.join(proj_folder, ".spinf.yaml"), "w+") as file:
            yaml_content = yaml.dump(SAVANNAH_PROJECT_INFORMATION, default_flow_style=False)
            pre_comment = "#\n# <savannah_framework:{version}>\n# !.spinf.yaml file\n\n"\
                .format(version=SAVANNAH_VERSION)

            file.write(pre_comment+yaml_content)
            print("Writing .spinf.yaml ... done")

        print("Project creation complete! Start the project by running `python manage.py run`")
        # TODO: this will only work if there are no subdirectories
        # TODO...An additional tweak is necessary to create empty
        # TODO...directories before copying files in case of nested directories.


