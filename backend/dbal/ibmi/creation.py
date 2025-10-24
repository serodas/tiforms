from django.db.backends.base.creation import BaseDatabaseCreation

class DatabaseCreation(BaseDatabaseCreation):
    def create_test_db(self, *args, **kwargs):
        # implementa si quieres DB de test, sino pasa
        return super().create_test_db(*args, **kwargs)
