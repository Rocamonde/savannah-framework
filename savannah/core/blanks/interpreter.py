#
# interpreter.py for project {project_name}
#
# Usage:
#
# class CommandInterpreter(BaseCommandInterpreter):
#     def __init__(self, sampling_manager):
#         super(CommandInterpreter, self).__init__(sampling_manager)
#
#         self.mapped_commands = {
#             # define mapped commands here, referencing CommandInterpreter
#             # Reference must not be executed.
#             # Key name must correspond to the name of a method.
#
#             'hello_world': self.hello_world,
#         }
#
#     def hello_world(self, arg1:str, arg2:int) -> str:
#         # Specify arguments types and function return type
#         # (if any) to be able to verify them in command interpretation.
#         # This functionality can be disabled by setting
#         # `self.verify_data_types = False`, though it is discouraged.
#
#         return "Hello World!"
#
#
# You can use class mix-ins to implement method blueprints easily.
# Many blueprints are readily available. You can import them by doing:
#
# from savannah.iounit.interpreter.blueprints import JSONBaseMixin
#
# Mix-ins have to be included as mother classes at any order but before
# the BaseCommandInterpreter class reference.
# Incorrect usage can result in invalid ORM schemes.
#

from savannah.iounit.interpreter import CommandInterpreter as BaseCommandInterpreter


class CommandInterpreter(BaseCommandInterpreter):
    def __init__(self, sampling_manager):
        super(CommandInterpreter, self).__init__(sampling_manager)

        self.mapped_commands = {
        }
