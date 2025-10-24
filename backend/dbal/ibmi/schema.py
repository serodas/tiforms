from django.db.backends.base.schema import BaseDatabaseSchemaEditor

class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    sql_create_table = "CREATE TABLE %(table)s (%(definition)s)"
    sql_delete_table = "DROP TABLE %(table)s"
    sql_rename_table = "RENAME TABLE %(old_table)s TO %(new_table)s"

    sql_create_column = "ALTER TABLE %(table)s ADD COLUMN %(column)s %(definition)s"
    sql_alter_column_type = "ALTER TABLE %(table)s ALTER COLUMN %(column)s SET DATA TYPE %(type)s"
    sql_alter_column_null = "ALTER TABLE %(table)s ALTER COLUMN %(column)s %(null)s"
    sql_alter_column_default = "ALTER TABLE %(table)s ALTER COLUMN %(column)s SET DEFAULT %(default)s"
    sql_delete_column = "ALTER TABLE %(table)s DROP COLUMN %(column)s"

    sql_create_index = "CREATE INDEX %(name)s ON %(table)s (%(columns)s)"
    sql_delete_index = "DROP INDEX %(name)s"

    sql_unique_constraint = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s UNIQUE (%(columns)s)"
    sql_delete_unique = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_foreign_key = (
        "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s "
        "FOREIGN KEY (%(column)s) REFERENCES %(to_table)s (%(to_column)s)"
    )
    sql_delete_foreign_key = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    def quote_value(self, value):
        """
        Convierte valores Python a formato SQL compatible con DB2 for i.
        """
        if value is None:
            return "NULL"
        if isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"
        if isinstance(value, bool):
            return "1" if value else "0"
        return str(value)
