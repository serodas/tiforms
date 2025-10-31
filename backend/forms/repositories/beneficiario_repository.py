from typing import Any, Dict
from forms.repositories.base_repository import BaseRepository
from forms.utils.db_helpers import rows_to_dict


class BeneficiarioRepository(BaseRepository):
    def get_beneficiario(
        self, search_param: str
    ) -> list[Dict[str, Any]] | Dict[str, Any] | None:
        try:
            search_pattern = f"%{search_param.upper()}%"
            sql = """SELECT 
                BENEFICIARIO.becodbene,
                BENEFICIARIO.tdtipdoc,
                BENEFICIARIO.benumdocbe,
                BENEFICIARIO.benombene,
                BENEFICIARIO.beapeprim,
                BENEFICIARIO.beapesegu 
                FROM BDSALUD.TBBDBENEFI BENEFICIARIO
                WHERE (BENEFICIARIO.benumdocbe LIKE ? OR 
                       trim(BENEFICIARIO.benombene) || ' ' || trim(BENEFICIARIO.beapeprim) || ' ' || trim(BENEFICIARIO.beapesegu) LIKE ?)
                AND BENEFICIARIO.becodestad='A' 
                ORDER BY BENEFICIARIO.benumdocbe ASC"""

            with self.conn.cursor() as cursor:
                cursor.execute(sql, [search_pattern, search_pattern])
                data = rows_to_dict(cursor, strip=True, single=False)
            return data
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            raise e
