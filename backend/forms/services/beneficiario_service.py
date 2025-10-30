from forms.repositories.beneficiario_repository import BeneficiarioRepository


class BeneficiarioService:
    def __init__(self, repository=None):
        self.repository = repository or BeneficiarioRepository()

    def search(self, search_param: str):
        if not search_param:
            raise ValueError("El parámetro de búsqueda es requerido")

        return self.repository.get_beneficiario(search_param)
