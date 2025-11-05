from typing import Any, Dict
from forms.repositories.base_repository import BaseRepository
from forms.utils.db_helpers import rows_to_dict


class ConsecutivosRecibosRepository(BaseRepository):
    def get_consecutivos_recibos(
        self, search_param: str
    ) -> list[Dict[str, Any]] | Dict[str, Any] | None:
        try:
            sql = """SELECT REC.MRCODCONS, 
            (SELECT CICODCITA FROM BDSALUD.TBAGCITAS CIT WHERE CIT.MRCODCONS=REC.MRCODCONS) CICODCITA, 
            REC.MRFECATE,
            REC.MRNUMPREFI,
            REC.MRNUMDOC
            FROM BDSALUD.TBFAMOVREC REC 
            WHERE REC.BECODBENE= ?
            AND DCTIPDOCUM='FA' 
            AND MOCODMOTIV=14 
            AND TSCODSERV<>'659' 
            AND MRCODCONS NOT IN (SELECT MRCODCONS  FROM BDSALUD.TBFADETCAR CAR WHERE CAR.MRCODCONS=REC.MRCODCONS) 
            AND MRFECATE  BETWEEN VARCHAR_FORMAT(ADD_MONTHS(CURRENT_DATE, -1), 'YYYYMMDD') AND VARCHAR_FORMAT(CURRENT_DATE, 'YYYYMMDD') 
            AND REC.MRNUMPREFI IS NOT NULL
            AND REC.MRNUMDOC IS NOT NULL
            AND REC.CACONSCAJA IS NOT NULL"""

            with self.conn.cursor() as cursor:
                cursor.execute(sql, [search_param])
                data = rows_to_dict(cursor, strip=True, single=False)
            return data
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            raise e
