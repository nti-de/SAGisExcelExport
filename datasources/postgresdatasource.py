import uuid
from typing import Tuple

from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsDataSourceUri

from . import databasehelper, postgreshelper
from .datasource import DataSource
from .featuresourceprovidertype import FeatureSourceProviderType


class PostgresDataSource(DataSource):
    def __init__(self, uri: QgsDataSourceUri):
        super().__init__(uri)
        # DataSource
        self.feature_source_provider_type = FeatureSourceProviderType.PostgreSQL

    def create_connection(self) -> Tuple[bool, str]:
        database_name = "sagis_" + uuid.uuid4().hex
        success, error_text = postgreshelper.create_connection(
            self.uri.host(), int(self.uri.port()), self.uri.database(),
            self.uri.username(), self.uri.password(), database_name
        )
        if not success:
            return False, error_text

        self.database = QSqlDatabase.database(database_name)
        self.database.setUserName(self.uri.username())
        self.database.setPassword(self.uri.password())

        return True, ""

    def select_into_dict_list(self, sql: str, null_value_to_none=True) -> list[dict]:
        result, self.error_text = databasehelper.select_into_dict_list(sql, self.database, null_value_to_none)
        return result

    def get_column_names(self, table_name: str, force_lower=False) -> list[str]:
        # PostgreSQL column names are always returned as lower.
        result, self.error_text = postgreshelper.get_column_names_with_database(self.database, table_name)
        return result

    def get_geom_columns(self, table_name: str, force_lower=False) -> list[str]:
        # PostgreSQL column names are always returned as lower.
        result, self.error_text = postgreshelper.get_geom_columns_with_database(table_name, self.database)
        return result

    def get_generic_select_statement(self, table_name: str, column_list=None) -> str:
        if not column_list:
            column_list = self.get_column_names(table_name)

        geom_columns = self.get_geom_columns(table_name)
        column_list = [f"ST_AsText({c}) AS {c}" if c in geom_columns else c for c in column_list]
        return f"SELECT {', '.join(column_list)} FROM {table_name}"
