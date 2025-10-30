from django.db import connections


class BaseRepository:
    def __init__(self, alias: str = "default") -> None:
        self.conn = connections[alias]
