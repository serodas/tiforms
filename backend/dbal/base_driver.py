# Clase base para drivers
class BaseDriver:
    """Clase base para drivers de DB2/AS400."""
    def connect(self, params):
        raise NotImplementedError("Debe implementar el método connect()")
