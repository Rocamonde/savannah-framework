class SamplingUnitNotRunning(Exception):
    def __init__(self, msg='', *args, **kwargs):
        msg = 'SamplingUnit module is not currently running. ({})'.format(msg)
        super().__init__(msg, *args, **kwargs)

class UndefinedEnvironment(Exception):
    def __init__(self, msg='', *args, **kwargs):
        msg = '{}'.format(msg)
        super().__init__(msg, *args, **kwargs)