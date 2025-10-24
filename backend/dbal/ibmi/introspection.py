from django.db.backends.base.introspection import BaseDatabaseIntrospection, TableInfo, FieldInfo

class DatabaseIntrospection(BaseDatabaseIntrospection):
    data_types_reverse = {
        # Mapeo básico DB2 → Django field
        "CHAR": "CharField",
        "VARCHAR": "CharField",
        "CLOB": "TextField",
        "GRAPHIC": "CharField",
        "VARGRAPHIC": "CharField",
        "BLOB": "BinaryField",
        "DECIMAL": "DecimalField",
        "NUMERIC": "DecimalField",
        "INTEGER": "IntegerField",
        "SMALLINT": "SmallIntegerField",
        "BIGINT": "BigIntegerField",
        "DATE": "DateField",
        "TIME": "TimeField",
        "TIMESTAMP": "DateTimeField",
    }

    def get_table_list(self, cursor):
        cursor.execute("SELECT TABLE_NAME, TABLE_TYPE FROM QSYS2.SYSTABLES")
        results = []
        for name, ttype in cursor.fetchall():
            if ttype in ("T", "L", "P"):   # T=table, L=logical, P=MQT
                type_code = "t"
            elif ttype == "V":
                type_code = "v"
            else:
                type_code = "t"  # fallback de seguridad
            results.append(TableInfo(name, type_code))
        return results

    def get_table_description(self, cursor, table_name, identity_check=True):
        """
        Devuelve metadata de columnas similar a cursor.description
        usando QSYS2.SYSCOLUMNS
        """
        
        sql = f"""
        SELECT COLUMN_NAME, SYSTEM_COLUMN_NAME, DATA_TYPE, LENGTH, NUMERIC_SCALE, IS_NULLABLE
        FROM QSYS2.SYSCOLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        cursor.execute(sql)

        description = []
        for colname, syscol, dtype, length, scale, is_nullable in cursor.fetchall():
            # Django espera FieldInfo
            description.append(FieldInfo(
                name=colname.strip(),
                type_code=dtype,
                display_size=length,
                internal_size=length,
                precision=scale if scale is not None else 0,
                scale=scale if scale is not None else 0,
                null_ok=(is_nullable == "YES"),
                default=None,
            ))
        return description

    def get_constraints(self, cursor, table_name):
        """
        Mínimo: retornar dict vacío.
        Si quieres, más adelante usas QSYS2.SYSREFCST y QSYS2.SYSCSTCOL.
        """
        return {}

    def get_sequences(self, cursor, table_name, table_fields=()):
        """
        DB2/IBM i normalmente no usa SEQUENCES sino identity columns.
        Devuelvo vacío por ahora.
        """
        return []
