# decorators.py
_registered_models = {}


def register_model_for_api(name=None):
    """
    Decorador para registrar modelos en la API genérica.

    Uso:
    @register_model_for_api('usuario')
    class Usuario(models.Model):
    """

    def decorator(model_class):
        model_name = name or model_class.__name__.lower()
        _registered_models[model_name] = model_class
        return model_class

    return decorator


def get_registered_models():
    """Obtener todos los modelos registrados"""
    return _registered_models.copy()


def get_model_by_name(model_name):
    """Obtener una clase de modelo por nombre"""
    return _registered_models.get(model_name)
