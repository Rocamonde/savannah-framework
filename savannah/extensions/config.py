
import json
import os
from typing import Dict, Union

from savannah.extensions.tupperware import box, Box


class Configuration:
    """
    **Usage:**

    # 1. To load an existing configuration file:
    >>> c = Configuration('/complete/path/to/file')
    # or:
    >>> c = Configuration()
    >>> c.load('/complete/path/to/file')
    # 2. To access the data:
    >>> c.data # --> Box
    >>> c.data.my_attr # --> Any
    # 3. To grab the data as dict:
    >>> c.as_dict # --> Dict
    # 4. To edit the data:
    >>> c.data["greeing"] = 'Hey, there!'
    # 5. To save changes:
    >>> c.save()
    # 6. To create a new config file from an object:
    >>> c = Configuration()
    >>> c.config_path = <config_path:str>
    >>> c.data = <my_object>
    >>> c.save()
    # 7. Or simply:
    >>> saved_config_instance = Configuration.new(<config_path:str>, <my_object:dict>)
    """

    def __init__(self, config_path: str = None):
        if config_path and not self.__path_exists(config_path):
            raise OSError("Invalid path to configuration file.")

        self.config_path = config_path

        self.__data: dict = self.__load() if config_path else dict()

    def __load(self, path: str = None):
        return json.load((path or self.config_path))

    def load(self, config_path: str):
        self.__init__(config_path)

    @staticmethod
    def __path_exists(path):
        return os.path.exists(path)

    def save(self):
        if self.__data and self.config_path:
            with open(self.config_path, 'wb') as file:
                json.dump(self.__data, file)
            return True
        return False

    @property
    def data(self) -> Box:
        """
        Returns the data in the form of a Box.
        Direct inplace changes are not allowed, to preserve its constant character
        (except when changing the entire dataset).
        To change a value use .set.
        """
        return box(self.__data)

    @property
    def as_dict(self) -> Dict:
        return self.__data

    @data.setter
    def data(self, value: Dict):
        self.__data = value

    @staticmethod
    def new(path, obj) -> 'Configuration':
        c = Configuration()
        c.config_path = path
        c.data = obj
        c.save()
        return c
