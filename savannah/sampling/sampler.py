import random
import os
from pandas import DataFrame
import datetime
from base64 import b32encode
from dataclasses import dataclass
import typing
from pickle import dump, dumps
from io import BytesIO

from savannah.asynchrony import threads
from savannah.sampling import drivers


__all__ = [
    "NoStorageMethodIOError", "SensorEnvironment", "SensorBaseReader", "SensorSampler", "SamplingManager", "Utils"
]

"""
######     Exceptions     ######
"""


class NoStorageMethodIOError(IOError):
    def __init__(self, *args, **kwargs):
        super(NoStorageMethodIOError, self).__init__(
            'No storage method specified. Can\'t save file',
            *args, **kwargs
        )


"""
######     Classes     ######
"""


@dataclass
class SensorEnvironment:
    init_stamp: str
    filename: str
    FILE_BASE: str


class SensorBaseReader:
    """
    Clase para leer información directamente del sensor.
    Esta clase solamente lee datos, no opera con ellos ni automatiza la lectura.
    Los datos son guardados en un archivo temporal con la fecha de creación estampada.
    Las unidades son siempre del Sistema Internacional de Unidades, excepto que se indique lo contrario o que se
    necesiten convertir primero.
    """

    stamp_format = '{0:%Y%m%d%H%M%S}'

    def __init__(self, sensor: drivers.Sensor, svdsk: bool = False, svmem: bool = True):

        if not (svdsk or svmem):
            raise NoStorageMethodIOError

        # El módulo sensor es de donde se muestrean los datos.
        self.sensor = sensor

        # Utilizar una lista es lo más eficiente porque:
        #     Es capaz de ampliar el espacio de manera dinámica con gran rapidez
        #     Al seleccionar un fragmento, se copia la referencia, no el valor
        #     Es sencillo manipular listas y convertirlas a arrays de numpy o a dataframes
        #
        # Nota: la primera fila de la lista es el título, y es el índice 0, por lo que los datos tienen numeración
        # 1-indexada.

        self.__data: list = [(*self.sensor.MAGNITUDES_VERBOSE, 'timestamp', ), ]
        self.__svdsk = svdsk
        self.__svmem = svmem

        if svmem:

            init_stamp = SensorBaseReader.stamp_format.format(datetime.datetime.now())
            filename = '{sensor}_{fname}.csv'.format(
                sensor=self.sensor.name(),
                fname=b32encode(init_stamp.encode()).decode()
            )

            self.environment = SensorEnvironment(
                init_stamp=init_stamp,
                filename=filename,
                FILE_BASE=os.path.join(settings.TEMP_PATH, filename)
            )

        # if svdsk:
        #    self.file: BytesIO = None

    def __sread(self):
        """
        Se comunica con el módulo sensor para tomar los datos del aparato.
        """
        # En principio el código podría transcurrir así;
        # pero depende de como sea la implementación precisa del sensor.

        # response, errors =   self.sensor.communicate()

        # Por ahora vamos a generar números aleatorios para esta implementación concreta.
        return (random.random() * 100, random.random())

    def update(self):
        # Rationale: se añade una tupla porque es más eficiente que una lista (el número de columnas no va a variar)
        # (la escalabilidad no es horizontal, sino vertical)
        self.__data.append((*self.__sread(), datetime.datetime.now()))

    def finalize(self):
        df = DataFrame(self.data)
        r1, r2 = (None, None)
        if self.svdsk:
            try:
                with open(self.environment.FILE_BASE, 'wb') as file:
                    dump(df, file)
                    r1 = self.environment.FILE_BASE
            except IOError:
                pass
        if self.svmem:
            r2 = BytesIO(dumps(df))

        del(self.__data, df)
        return (r1, r2) if (r1 and r2) else (r1 or r2)

    def retrieve_last(self, key):
        return {'last_key': len(self.data)-1,
                'data': self.data[(key+1 if key else 0):]}

    @property
    def svdsk(self) -> bool:
        return self.__svdsk

    @property
    def svmem(self) -> bool:
        return self.__svmem

    @property
    def data(self) -> typing.List[typing.Tuple]:
        return self.__data


class SensorSampler(threads.ThreadedLoop):

    """
    Esta clase permite crear un thread como un daemon que corre simultáneamente con el resto del código.
    El thread incorpora un loop que está constantemente sampleando datos excepto que se ejecute el comando
    self.stop(). Si esto último es así, si ya se ha entrado en el loop en el momento de ejecución y el programa
    está durmiendo, esperará a que termine para parar. Esto puede modificarse y matar el proceso, pero como el archivo
    de datos se guarda de manera independiente, no es necesario para seguir procesando la información.

    """

    def __init__(self, reader: SensorBaseReader, sampling_frequency=None):
        self.reader = reader

        # Sampling frequency can be specified in instantiation
        # or default frequency falls back.
        if not sampling_frequency:
            self.frequency = self.reader.sensor.SENSOR_DEFAULT_FREQUENCY

        # Boundary conditions for valid frequency
        elif isinstance(sampling_frequency, (int, float)) and \
                0 < sampling_frequency <= self.reader.sensor.SENSOR_DEFAULT_FREQUENCY:
            self.frequency = sampling_frequency
        else:
            raise ValueError("Sampling frequency must be an integer or float in the interval ]0, {max}]".format(
                max=self.reader.sensor.SENSOR_DEFAULT_FREQUENCY))

        super(SensorSampler, self).__init__(interval=1/self.frequency, name=self.reader.sensor.name())

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
    samplers = lambda sensors_list: [SensorSampler(SensorBaseReader(_)) for _ in sensors_list]



