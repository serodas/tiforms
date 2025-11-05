from forms.repositories.consecutivos_recibos_repository import (
    ConsecutivosRecibosRepository,
)


class ConsecutivosRecibosService:
    def __init__(self, repository=None):
        self.repository = repository or ConsecutivosRecibosRepository()

    def search(self, search_param: str):
        if not search_param:
            raise ValueError("El parámetro de búsqueda es requerido")

        response = []
        results = self.repository.get_consecutivos_recibos(search_param)

        if not results:
            return response

        for result in results:
            response.append(
                {
                    "value": int(result.get("mrcodcons")),  # type: ignore
                    "label": f"Interno: {result.get('mrcodcons')} - Cod.Cita: {0 if result.get('cicodcita') == None else result.get('cicodcita')}",  # type: ignore
                }
            )
        return response
