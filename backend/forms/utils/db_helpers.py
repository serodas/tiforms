from typing import Any, Dict, List, Optional, Union
from django.db.backends.utils import CursorWrapper


def rows_to_dict(
    cursor: CursorWrapper, strip: bool = True, single: bool = False
) -> Union[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Convierte el resultado de un cursor a lista de diccionarios.

    Args:
        cursor: Cursor después de ejecutar el SQL.
        strip (bool): Si es True, hace strip() a los strings.
        single (bool): Si es True, retorna solo un dict en lugar de lista.

    Returns:
        - Si single=False → List[Dict[str, Any]]
        - Si single=True  → Optional[Dict[str, Any]]
    """
    columns: List[str] = [col[0].lower() for col in cursor.description]
    rows = cursor.fetchall()

    data: List[Dict[str, Any]] = []
    for row in rows:
        row_dict: Dict[str, Any] = dict(zip(columns, row))
        if strip:
            row_dict = {
                k: v.strip() if isinstance(v, str) else v for k, v in row_dict.items()
            }
        data.append(row_dict)

    if single:
        return data[0] if data else None
    return data
