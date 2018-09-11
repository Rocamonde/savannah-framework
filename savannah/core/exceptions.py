class SamplingUnitNotRunning(Exception):
    def __init__(self, msg='', *args, **kwargs):
        msg = 'SamplingUnit module is not currently running. ({})'.format(msg)
        super().__init__(msg, *args, **kwargs)

class UndefinedEnvironment(Exception):
    pass

class MisconfiguredSettings(Exception):
    missing = 'Missing required configuration properties'
    json_format = 'settings.json file does not have a valid JSON format'
    data_types = 'Invalid data types: data types do not match specifications or are not convertible'
    invalid_path = ('Invalid relative path: specified path to file or directory does not exist.\n'
                    'Paths in settings.json are always relative to the settings file directory.\n'
                    'Did you mistakenly specify an absolute path?')
