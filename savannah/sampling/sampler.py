import os, sys, random, pickle, datetime, csv
from base64 import b32encode
from dataclasses import dataclass
from io import BytesIO
from typing import *

from pandas import DataFrame
# TODO CHANGE THIS
from multiprocessing import Queue

from savannah.asynchrony import threads
from savannah.sampling import drivers
from savannah.core.exceptions import MisconfiguredSettings

# TODO: what's left: implement periodic uploder/file saver.

__all__ = [
    "NoStorageMethod",
    "SensorEnvironment", "SensorBaseReader", "SensorSampler", "SamplingManager", "Utils"
]

#
# Exceptions
#


class NoStorageMethod(IOError):
    def __init__(self, *args, **kwargs):
        super(NoStorageMethod, self).__init__(
            'No storage method specified. Can\'t save file',
            *args, **kwargs
        )


#
# Classes
#


@dataclass
class SensorEnvironment:
    init_stamp: str
    filename: str
    filepath: str


# TODO: check this in LINUX (what os.W_OK does)
def _eval_path(a, b):
    if sys.platform == 'win32':
        return a and b
    return b

class SensorBaseReader:
    """
    Clase para leer información directamente del sensor.
    Esta clase solamente lee datos, no opera con ellos ni automatiza la lectura.
    Los datos son guardados en un archivo temporal con la fecha de creación estampada.
    Las unidades son siempre del Sistema Internacional de Unidades, excepto que se indique lo contrario o que se
    necesiten convertir primero.
    """

    stamp_format = '{0:%Y%m%d%H%M%S}'

    def __init__(self, sensor: drivers.Sensor, save_to_disk: bool = None, save_in_mem: bool = None):
        from savannah.core import settings

        # Using a lists provides:
        #   - Fast resize (no need for pre-allocation)
        #   - Pass-by-reference slicing
        #   - Easy data conversion
        # Note: data is 1-indexed because first row are the column titles.

        self.__data: list = [(*self.sensor.MAGNITUDES_VERBOSE, 'timestamp',), ]
        self.sensor = sensor
        self.__dump: bool = False

        #
        # Data storage configuration
        #

        cnf = self.sensor.settings._asdict()

        try:

            # Logical order of decision:
            #   1. Sensor settings if exists (defined in settings.json, loaded externally)
            #   2. SensorBaseReader init arguments if exists
            #   3. Settings fallback if exists
            #       - If settings not exists, raise MisconfiguredSettings
            #
            # A last option could be added, which would be a framework default.
            # This would catch the AttributeError

            # Ternary operator must explicitly evaluate None identity since we are handling bools
            self.__svdsk = cnf.get('svdsk',
                (save_to_disk if save_to_disk is None else settings.workflow.temp_data.enable))

            self.__svmem = cnf.get('svmem',
                (save_in_mem if save_in_mem is None else settings.workflow.live_upload))


            if not (self.__svdsk or self.__svmem):
                # Technically, there could be a storage method if this is implemented explicitly.
                # However, in principle the sensor must either save to a file to then upload or
                # Upload real time. To modify this, one should catch the error in instantiation.
                raise NoStorageMethod
            else:
                self.__dump = True

            if save_to_disk:
                temp_path_base = os.path.join(settings.BASEDIR, settings.workflow.temp_data.path)

                init_stamp = SensorBaseReader.stamp_format.format(datetime.datetime.now())
                filename = '{sensor}_{fname}.csv'.format(
                    sensor=self.sensor.name(),
                    fname=b32encode(init_stamp.encode()).decode()
                )

                temp_path = os.path.join(temp_path_base, filename)

                if not _eval_path(os.path.exists(temp_path_base), os.access(temp_path_base, os.W_OK)):
                    raise IOError("Temporary path does not exist or is not writable.")

                self.environment = SensorEnvironment(
                    init_stamp=init_stamp,
                    filename=filename,
                    filepath=temp_path,
                )
                # Virtual file for real-time writing
                self.file: BytesIO = BytesIO()

            if save_in_mem:
                self.queue = Queue()

        except AttributeError:
            raise MisconfiguredSettings("Missing required configuration properties.")

    def __sread(self):
        """
        Se comunica con el módulo sensor para tomar los datos del aparato.
        """
        # En principio el código podría transcurrir así;
        # pero depende de como sea la implementación precisa del sensor.

        # response, errors =   self.sensor.communicate()

        # TODO: replace this
        return (random.random() * 100, random.random())

    def update(self):
        # Rationale: se añade una tupla porque es más eficiente que una lista (el número de columnas no va a variar)
        # (la escalabilidad no es horizontal, sino vertical)
        read = (*self.__sread(), datetime.datetime.now())
        self.__data.append(read)
        if self.__dump:
            self.dump(read)


    def retrieve_last(self, key):
        return {'last_key': len(self.data)-1,
                'data': self.data[(key+1 if key else 0):]}

    def dump(self, obj: Iterable):
        if self.__svdsk:
                # this always appends
                _writer = csv.writer(self.file, delimiter=',')
                _writer.writerow(obj)
        if self.__svmem:
            self.queue.put(obj)

    @property
    def svdsk(self) -> bool: return self.__svdsk

    @property
    def svmem(self) -> bool: return self.__svmem

    @property
    def data(self) -> typing.List[typing.Tuple]: return self.__data


class SensorSampler(threads.ThreadedLoop):

    """
    Esta clase permite crear un thread como un daemon que corre simultáneamente con el resto del código.
    El thread incorpora un loop que está constantemente sampleando datos excepto que se ejecute el comando
    self.stop(). Si esto último es así, si ya se ha entrado en el loop en el momento de ejecución y el programa
    está durmiendo, esperará a que termine para parar. Esto puede modificarse y matar el proceso, pero como el archivo
    de datos se guarda de manera independiente, no es necesario para seguir procesando la información.

    """

    def __init__(self, reader: SensorBaseReader):
        self.reader = reader
        self.sampling_frequency = self.reader.sensor.settings._asdict().get(
            'FREQUENCY',
            self.reader.sensor.SENSOR_DEFAULT_FREQUENCY)

        # Boundary conditions for valid frequency
        if not isinstance(self.sampling_frequency, (int, float)) and \
                0 < self.sampling_frequency <= self.reader.sensor.SENSOR_DEFAULT_FREQUENCY:
            raise ValueError("Sampling frequency must be an integer or float in the interval ]0, {max}]".format(
                max=self.reader.sensor.SENSOR_MAX_FREQUENCY))

        super(SensorSampler, self).__init__(interval=1/self.sampling_frequency, name=self.reader.sensor.name())

    def task(self):
        self.reader.update()


class SamplingManager(threads.ReverseManagerMixin):
    def start_all(self):
        for sampler in self.wrappers_list:
            sampler.start()


class Utils:
    # En condiciones normales, la frecuencia por defecto del sensor debería ser la apropiada,
    # excepto que sea estrictamente necesario especificar una personalizada.
    # Por ello no se permite la inclusión del parámetro frecuencia.
    make_sampler = lambda sensor: SensorSampler(SensorBaseReader(sensor))
    make_samplers = lambda sensor_list: [Utils.make_sampler(_) for _ in sensor_list]



