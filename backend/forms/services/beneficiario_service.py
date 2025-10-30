from forms.repositories.beneficiario_repository import BeneficiarioRepository


class BeneficiarioService:
    def __init__(self, repository=None):
        self.repository = repository or BeneficiarioRepository()

    def search(self, search_param: str):
        if not search_param:
            raise ValueError("El parámetro de búsqueda es requerido")

        response = []
        results = self.repository.get_beneficiario(search_param)

        if not results:
            return response

        for result in results:
            response.append(
                {
                    "value": int(result.get("becodbene")),  # type: ignore
                    "label": f"{result.get('benombene')} {result.get('beapeprim')} {result.get('beapesegu')}",  # type: ignore
                }
            )
        return response
