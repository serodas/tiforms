import pyodbc
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.features import BaseDatabaseFeatures
from dbal.ibmi_driver import IbmiDriver
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor
from .introspection import DatabaseIntrospection
from .creation import DatabaseCreation
from .client import FakeClient
from .features import FakeFeatures


class IbmiCursorWrapper:
    def __init__(self, real_cursor, ops):
        self.cursor = real_cursor
        self.ops = ops
        self._lastrowid = None

    def prepare_sql(self, sql, params):
        """
        Convierte %s a ? y transforma tipos incompatibles con DB2.
        """
        if params:
            new_params = []
            for p in params:
                if isinstance(p, bool):
                    new_params.append(1 if p else 0)
                else:
                    new_params.append(p)
            sql = sql.replace("%s", "?")
            return sql, new_params
        return sql, params

    def execute(self, sql, params=None):
        sql, params = self.prepare_sql(sql, params)

        if params:
            result = self.cursor.execute(sql, params)
        else:
            result = self.cursor.execute(sql)

        # Captura último ID generado
        if sql.strip().upper().startswith("INSERT"):
            try:
                self.cursor.execute("SELECT IDENTITY_VAL_LOCAL() FROM SYSIBM.SYSDUMMY1")
                self._lastrowid = self.cursor.fetchone()[0]
            except Exception:
                self._lastrowid = None

        return result

    def executemany(self, sql, param_list):
        new_param_list = []
        for params in param_list:
            _, new_params = self.prepare_sql(sql, params)
            new_param_list.append(new_params)

        result = self.cursor.executemany(sql, new_param_list)
        self._lastrowid = None
        return result

    @property
    def lastrowid(self):
        return self._lastrowid

    # --- Compatibilidad con Django ORM ---
    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return iter(self.cursor)

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)


# ====================================================
# DatabaseWrapper personalizado
# ====================================================
class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = "ibmi"
    display_name = "IBM i Access"

    features_class = BaseDatabaseFeatures
    ops_class = DatabaseOperations
    SchemaEditorClass = DatabaseSchemaEditor
    introspection_class = DatabaseIntrospection
    creation_class = DatabaseCreation
    client_class = FakeClient

    paramstyle = "qmark"

    class Database:
        Error = pyodbc.Error
        Warning = pyodbc.Warning
        InterfaceError = pyodbc.InterfaceError
        DatabaseError = pyodbc.DatabaseError
        DataError = pyodbc.DataError
        OperationalError = pyodbc.OperationalError
        IntegrityError = pyodbc.IntegrityError
        InternalError = pyodbc.InternalError
        ProgrammingError = pyodbc.ProgrammingError
        NotSupportedError = pyodbc.NotSupportedError

    def __init__(self, settings_dict, alias="default", *args, **kwargs):
        super().__init__(settings_dict, alias, *args, **kwargs)
        self.ops = self.ops_class(self)

    @property
    def operators(self):
        return self.ops.operators

    def _set_autocommit(self, autocommit):
        if self.connection:
            self.connection._conn.autocommit = autocommit
        self.connection_autocommit = autocommit

    def get_connection_params(self):
        return {
            "DSN": self.settings_dict.get("NAME"),
        }

    def get_new_connection(self, conn_params):
        driver = IbmiDriver()
        return driver.connect(conn_params, test_only=False)

    def ensure_connection(self):
        if self.connection is None:
            params = self.get_connection_params()
            self.connection = self.get_new_connection(params)

    def create_cursor(self, name=None):
        self.ensure_connection()
        real_cursor = self.connection.cursor()
        # Devolvemos el cursor envuelto para interceptar execute / executemany
        return IbmiCursorWrapper(real_cursor, self.ops)

    def _commit(self):
        if self.connection:
            self.connection.commit()

    def _rollback(self):
        if self.connection:
            self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
