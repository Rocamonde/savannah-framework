#
# Interpreter blueprints
#
# Place for pre-defined interpreter methods in
# the form of class mix-ins.
#

import json

from .interpreter import CommandInterpreter


class JSONUpdatesMixin(CommandInterpreter):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.mapped_commands['updates'] = self.updates

    def updates(self, last_key: dict = None):
        """
        Data is searched through dynamic bounds to allow for
        something similar to API pagination.
        List slicing does not create memory duplicates; only when
        it is dumped to JSON.

        This is useful for web interfaces.
        """

        last_key = last_key or dict()
        response = {sensor_name: sampler.reader.retrieve_last(last_key.get(sensor_name, None))
                    for sensor_name, sampler in self.sampling_manager.processes_dict.items()}

        # Careful: dates are not dumped to JSON standard format. It must be parsed.
        # TODO: change this
        return json.dumps(response, default=str)

