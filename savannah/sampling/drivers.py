from typing import NamedTuple

__all__ =  ["Sensor", "PortNotOpenError"]

class PortNotOpenError(Exception):
    # Implement appropriate error message to raise when port is not open
    pass

# TODO: buscar manera de implementar esta clase con cada driver específico sin tener que reescribir todo el código



class Sensor:
    """
    Clase genérica de un sensor. Puede abrir puertos, cerrarlos y leer información de ellos.
    Debe ser extendido para poder implementarlo.
    """

    SENSOR_MAX_FREQUENCY: float = None
    SENSOR_DEFAULT_FREQUENCY: float = None

    MAGNITUDES_VERBOSE: tuple = None

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    def __init__(self, settings: NamedTuple = None):
        # self.port = None
        self.__is_open = False
        self.settings: NamedTuple = None


    @property
    def is_open(self):
        # No vamos a implementar un setter para que no pueda cambiarse desde fuera el bool del puerto sin haber cerrado
        # el puerto en realidad.
        return self.__is_open

    def open(self):
        """
        Método para abrir el puerto
        """
        try:
            # self.port.open()
            self.__is_open = True
        except:
            # Handle here error raising due to any error when opening the port
            pass

    def read(self):
        """
        Método para leer del puerto
        """
        try:
            assert(self.is_open)
            # result = self.port.read()
            # Incluir aquí un método para leer del puerto
            # return result
        except AssertionError:
            raise PortNotOpenError
        except:
            # Handle here error raising due to any error while reading data from the port
            pass

    def close(self):
        """
        Método para cerrar el puerto
        """
        try:
            # self.port.close()
            self.__is_open = False
        except:
            # Incluir aquí el manejo de posibles errores cerrar el puerto
            pass




