from typing import Tuple

from PyQt5.QtCore import QVariant
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def select_into_dict_list(sql: str, database: QSqlDatabase, null_value_to_none=False) -> Tuple[list[dict], str]:
    result = []
    if not database.isOpen():
        database.open()
    query = QSqlQuery(database)
    if not query.exec(sql):
        return result, query.lastError().text()
    else:
        columns = query.record().count()
        while query.next():
            row = {}
            for i in range(columns):
                column_name = query.record().fieldName(i)
                # row[column_name] = query.value(i)
                row[column_name] = None if null_value_to_none and isinstance(query.value(i), QVariant) and query.value(i).isNull() else query.value(i)
            result.append(row)

    return result, ""
