from typing import Optional, Tuple

from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsDataSourceUri, QgsSettings

from . import databasehelper

POSTGRESQL_CONNECTION_PATH = "PostgreSQL/connections"


def create_connection(host: str, port: int, database: str, user: str, password: str, q_database_name="") -> Tuple[bool, str]:
    con = QSqlDatabase.addDatabase("QPSQL", q_database_name)
    con.setHostName(host)
    con.setPort(port)
    con.setDatabaseName(database)
    if not con.open(user, password):
        return False, con.lastError().text()
    return True, ""


def create_uri(connection_name: str, user: str, password: str) -> Optional[QgsDataSourceUri]:
    # TODO: Use QgsProviderRegistry.instance().providerMetadata('postgres').connections() instead
    if not connection_name:
        return None
    settings = QgsSettings()
    host = settings.value(f"{POSTGRESQL_CONNECTION_PATH}/{connection_name}/host", "")
    port = settings.value(f"{POSTGRESQL_CONNECTION_PATH}/{connection_name}/port", "")
    database = settings.value(f"{POSTGRESQL_CONNECTION_PATH}/{connection_name}/database", "")
    uri = QgsDataSourceUri()
    uri.setConnection(host, port, database, user, password)
    return uri


def get_column_names_with_database(database: QSqlDatabase, table_name: str, table_schema="public") -> Tuple[list[str], str]:
    # result = []
    sql = f"""SELECT column_name
FROM information_schema.columns
WHERE table_schema = '{table_schema.lower()}'
AND table_name = '{table_name.lower()}'
ORDER BY ordinal_position"""

    # if not database.isOpen():
    #     database.open()
    # query = QSqlQuery(database)
    # if not query.exec(sql):
    #     loggerutils.log_error(logger, query.lastError().text())
    # else:
    #     while query.next():
    #         result.append(query.value(0))
    # return result

    result_dicts, error_text = databasehelper.select_into_dict_list(sql, database)
    result = [list(r.values())[0] for r in result_dicts]
    return result, error_text


def get_geom_columns_with_database(table_name: str, database: QSqlDatabase) -> Tuple[list[str], str]:
    sql = f"""SELECT f_geometry_column FROM geometry_columns WHERE f_table_name = '{table_name.lower()}'"""
    result, error_text = databasehelper.select_into_dict_list(sql, database)
    return [d.get("f_geometry_column") for d in result], error_text


# Unused
# def get_primary_key_column(host: str, port: int, database: str, user: str, password: str, table: str, schema="public") -> Optional[str]:
#     """Returns the primary key column of the given table."""
#
#     temp_name = "sagis_" + uuid.uuid4().hex
#
#     if not create_connection(host, port, database, user, password, q_database_name=temp_name):
#         return None
#
#     con = QSqlDatabase.database(temp_name)
#
#     query = QSqlQuery(con)
#
#     query.prepare(f"""select kc.column_name
# from information_schema.table_constraints tc
#   join information_schema.key_column_usage kc
#     on kc.table_name = tc.table_name and kc.table_schema = tc.table_schema and kc.constraint_name = tc.constraint_name
# where tc.constraint_type = 'PRIMARY KEY'
#   and kc.ordinal_position is not null
#   and tc.table_schema = ?
#   and tc.table_name = ?""")
#
#     query.addBindValue(schema)
#     query.addBindValue(table)
#
#     if not query.exec():
#         loggerutils.log_error(logger, query.lastError().text())
#         con.close()
#         QSqlDatabase.removeDatabase(con.connectionName())
#         return None
#
#     query.next()
#     primary_key_column = query.value(0)
#
#     if query.next():
#         loggerutils.log_warning(logger, f"Table '{table}' has more than one primary key column; '{primary_key_column}' will be used")
#
#     con.close()
#     QSqlDatabase.removeDatabase(con.connectionName())
#     return primary_key_column
