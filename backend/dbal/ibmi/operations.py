from django.db.backends.base.operations import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    paramstyle = "qmark"
    compiler_module = "django.db.models.sql.compiler"
    # Diccionario obligatorio para lookups (filtros de Django)
    operators = {
        "exact": "= %s",
        "iexact": "LIKE %s",
        "contains": "LIKE %s",
        "icontains": "LIKE %s",
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s",
        "istartswith": "LIKE %s",
        "endswith": "LIKE %s",
        "iendswith": "LIKE %s",
        "range": "BETWEEN %s AND %s",
        "isnull": "IS NULL",
    }

    def quote_name(self, name):
        """
        Encierra nombres de tablas y columnas entre comillas dobles
        para que se respeten mayúsculas/minúsculas y no choquen con keywords.
        """
        if name.startswith('"') and name.endswith('"'):
            return name
        return f'"{name}"'

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        """
        Genera las sentencias SQL para vaciar todas las tablas.
        DB2 for i permite DELETE FROM en lugar de TRUNCATE.
        """
        sql = []
        for table in tables:
            sql.append(f"DELETE FROM {self.quote_name(table)}")
        return sql

    def limit_offset_sql(self, low_mark, high_mark):
        """
        Traduce el slicing de QuerySets (OFFSET / LIMIT).
        En DB2 for i moderno se soporta FETCH FIRST y OFFSET.
        """
        sql = ""
        if high_mark is not None:
            # Si hay límite superior
            if low_mark:
                sql = f" OFFSET {low_mark} ROWS FETCH NEXT {high_mark - low_mark} ROWS ONLY"
            else:
                sql = f" FETCH FIRST {high_mark} ROWS ONLY"
        elif low_mark:
            # Solo OFFSET (sin límite)
            sql = f" OFFSET {low_mark} ROWS"
        return sql

    def adapt_datetimefield_value(self, value):
        """
        Convierte valores de Python datetime a formato DB2 i.
        """
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    def adapt_timefield_value(self, value):
        """
        Convierte valores de Python time a formato HH:MM:SS.
        """
        if value is None:
            return None
        return value.strftime("%H:%M:%S")

    def random_function_sql(self):
        """
        Retorna la función nativa de random para DB2.
        """
        return "RAND()"

    def no_limit_value(self):
        """
        Valor especial para indicar 'sin límite'.
        """
        return None

    def prep_for_like_query(self, x):
        """
        Escapa caracteres especiales en consultas LIKE.
        """
        return str(x).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def combine_expression(self, connector, sub_expressions):
        """
        Cómo se combinan expresiones en consultas complejas.
        """
        return f" {connector} ".join(sub_expressions)

    def savepoint_create_sql(self, sid):
        return f"SAVEPOINT {self.quote_name(sid)} ON ROLLBACK RETAIN CURSORS"

    def savepoint_rollback_sql(self, sid):
        return f"ROLLBACK TO SAVEPOINT {self.quote_name(sid)}"

    def savepoint_commit_sql(self, sid):
        # En DB2 no siempre es necesario, pero lo dejamos
        return f"RELEASE SAVEPOINT {self.quote_name(sid)}"

    def tablespace_sql(self, tablespace, inline=False):
        """
        DB2 for i no usa TABLESPACE como Oracle/Postgres,
        devolvemos string vacío.
        """
        return ""

    def conditional_expression_supported_in_where_clause(self, expression):
        # DB2 no soporta booleanos directamente en WHERE
        return False

    def adapt_boolean_field_value(self, value):
        """Convierte booleanos a 1/0 para DB2"""
        return 1 if value else 0
