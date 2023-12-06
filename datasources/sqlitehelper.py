from typing import Tuple

from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsDataSourceUri

from . import databasehelper


def create_connection(database: str, q_database_name="") -> Tuple[bool, str]:
    con = QSqlDatabase.addDatabase("QSQLITE", q_database_name)
    con.setDatabaseName(database)
    if not con.open():
        return False, con.lastError().text()
    return True, ""


def create_uri(database_path: str) -> QgsDataSourceUri:
    uri = QgsDataSourceUri()
    uri.setDatabase(database_path)
    return uri


def get_column_names(database: QSqlDatabase, table_name: str, type_="", force_lower=False) -> Tuple[list[str], str]:
    # result = []
    # Ignore geoemtry columns for SQLite
    where = " WHERE type != 'FDO_GEOMETRY_as_blob'"
    where = f"{where} AND type = '{type_}'" if type_ else where
    sql = f"SELECT name FROM pragma_table_info('{table_name}'){where}"

    # if not database.isOpen():
    #     database.open()
    # query = QSqlQuery(database)
    # if not query.exec(sql):
    #     loggerutils.log_error(logger, query.lastError().text())
    # else:
    #     while query.next():
    #         value = query.value(0)
    #         value = value.lower() if force_lower and isinstance(value, str) else value
    #         result.append(value)
    # return result

    result_dicts, error_text = databasehelper.select_into_dict_list(sql, database)
    result = [list(r.values())[0] for r in result_dicts]
    if force_lower:
        result = [c.lower() for c in result]
    return result, error_text
