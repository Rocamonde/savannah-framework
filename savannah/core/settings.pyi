#
# Stub file for settings
#


from typing import NamedTuple, Union, Callable

#
# **Format spacing:**
#   - Before class: 2 empty lines
#   - Inside the class, below the name: 0 empty lines | 1 empty line is child is class
#   - After the class, 1 empty line if nested classes, 0 if none
#

# Do NOT start a variable name with two underscores,
# Or adequate settings file will not be generated.


# *.*.*-----------------------------------------------------------------------------------*.*.*
#<begin>

    #
    #  **Global notes**
    #
    # host:str: either 'local' -> 127.0.0.1, or 'remote' (defaults to static ip)
    #   There is no need knowing the remote IP in the configuration file.
    #   A different function will take care of configuring IPs
    #   and serving them in place of 'remote' str.
    # path:str: always relative to settings file (absolute paths not allowed in this version).
    #


# General workflow configuration
class Workflow(NamedTuple):
    live_upload: bool = True                        # Uploads data at real-time performance.
    require_auth: bool = False                      # Includes the AuthUnit module.


    class TempData(NamedTuple):                     # Temporary files.
        enable: bool = False
        path: str = 'temp/'
        frequency: Union[None, float] = None        # None for auto or float in seconds
    temp_data: TempData = TempData()


    class Server(NamedTuple):                       # This is the CPUServer configuration.

        class Address(NamedTuple):
            host: str = 'local'
            port: int = 5555
        address: Address = Address()

    server: Server = Server()


    class LocalUI(NamedTuple):
        enabled: bool = False

        class Address(NamedTuple):
            host: str = 'local'
            port: bool = 8000
        address = Address()

    localui: LocalUI = LocalUI()

workflow: Workflow = Workflow()


# Drivers for enabled sensors must be defined in drivers.py
enabled_sensors: list = []

class Info(NamedTuple):
    project_name: str = 'Savannah'
    project_owner: str = 'Juan Carlos Rocamonde'
info: Info = Info()

#
# Include enabled fields for JSON generation
#

enabled_fields = (
    'workflow', 'enabled_sensors', 'info',
)

#<end>
# *.*.*-----------------------------------------------------------------------------------*.*.*

MisconfiguredSettings: Exception
BASEDIR: str
CONFIG_PATH: str


# Leave these lines to allow dynamic generation of the JSON file
#

if __name__ == '__main__':
    import json
    import sys
    sys.path.append('C:\\Users\\pc\\PyCharmProjects\\teleboard\\src\\savannah\\')
    from savannah.extensions.tupperware import unbox

    __vars = {key: unbox(val) for key, val in globals().items() if key in enabled_fields}

    print(json.dumps(__vars, indent=4))

