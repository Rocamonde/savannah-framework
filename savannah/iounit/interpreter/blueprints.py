#
# Interpreter blueprints
#
# Place for pre-defined interpreter methods in
# the form of class mix-ins.
#

import json

from .interpreter import CPUInterpreter


class JSONUpdatesMixin(CPUInterpreter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapped_commands.update({'updates': self.updates })

    def updates(self, last_key: dict = None):
        """
        Data is searched through dynamic bounds to allow for
        something similar to API pagination.
        List slicing does not create memory duplicates; only when
        it is dumped to JSON.

        """
        last_key = last_key or dict()
        response = {sensor_name: sampler.reader.retrieve_last(last_key.get(sensor_name, None))
                    for sensor_name, sampler in self.sampling_manager.wrappers_dict.items()}

        # Note: dates are dumped with a standard Python format.
        # This format is not automatically recognised when dates are parsed back
        # (they're considered strings).
        # Since there are different conventions on the date format, and
        # JSON does not explicitly specify one, I've chosen to let dates
        # remain in this format until any other convention is agreed.

        return json.dumps(response, default=str)

