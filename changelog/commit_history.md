# Commit history

When miscellaneous changes are implemented into a commit, 
I will make reference to them in this file,
to be able to expand on them further than a brief compilation
in the commit message.


#### Commit [1c0165bb0564b5a6d1e921d4f1830d68bb8fc1f7](https://github.com/Rocamonde/savannah-framework/commit/1c0165bb0564b5a6d1e921d4f1830d68bb8fc1f7)

 - Rollback to using standard multiprocessing. Provides easier way to debug.

 - Restructured cli_commands folder. Difficult to write command instructions in a file that is huge. Prefer to write a file for every command.

 - Now able to run tests from manage. Either a file or a folder. Supports output to files.

 - Added testenv folder for easier testing.

#### Commit [826c3b9d903627718807c239a106358579fc8cc4](https://github.com/Rocamonde/savannah-framework/commit/826c3b9d903627718807c239a106358579fc8cc4)

 - Content of CLI command actions (particularly `run.py`) was moved to a separate file. New folder created: `core/app`. `__init__.py` file contains App definition, `units.py` file was moved to app folder to improve organisation.
 
 - This is to facilitate code organisation and to enable the creation of scripts (especially for test units) that start and stop the server programatically without needing a CLI interface.
 
 - Added TODO about the importance of creating a closing method that saves files safely and stops the server. Another way of forcefully killing it should also be developed.
 
 - CPUServer can now be closed even if acceptance call is blocking since we created a mock call to stop that and make the loop crash and the thread join.
 
 - CL logging format was changed to make something better looking.
 
 - Translated some comment blocks from Spanish to English (consistency) and improved explanation on some sections.
 
 - Environment folder was deleted, now environments can be created dynamically through command line script `savannah` that is installed with standard installation.
 
 - Fixed some errors regarding file creation due to how the current working directory was fetched (we assumed file directory was same as cwd but that is wrong since files are copied to other folders after installation).
 
 - Fixed errors regarding host/port recognition and created type enforcement for `argparse` to facilitate error handling.
 
 - Moved most settings import to execution and not to the top level scope to prevent errors.
