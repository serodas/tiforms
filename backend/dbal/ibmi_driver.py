import pyodbc
from .base_driver import BaseDriver
from .connection import Connection
from .exceptions import Db2ConnectionError

class IbmiDriver(BaseDriver):
    """Driver DB2/AS400 usando pyodbc."""

    def connect(self, params, test_only=False):
        if test_only:
            # Devuelve un connection fake
            return FakeConnection()
        try:
            dsn_name = params.get('DSN', 'PROD')
            conn = pyodbc.connect(f"DSN={dsn_name}", autocommit=True)
            return Connection(conn)
        except Exception as e:
            raise Db2ConnectionError(str(e))

class FakeConnection:
    def cursor(self): return self
    def execute(self, q, p=None): return None
    def fetchall(self): return []
    def commit(self): pass
    def rollback(self): pass
    def close(self): pass