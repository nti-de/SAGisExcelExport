import uuid
from typing import Tuple

from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsDataSourceUri

from . import databasehelper, sqlitehelper
from .datasource import DataSource
from .featuresourceprovidertype import FeatureSourceProviderType


class SqliteDataSource(DataSource):
    def __init__(self, uri: QgsDataSourceUri):
        super().__init__(uri)
        # DataSource
        self.feature_source_provider_type = FeatureSourceProviderType.Sqlite

    def create_connection(self) -> Tuple[bool, str]:
        database_name = "sagis_" + uuid.uuid4().hex
        success, error_text = sqlitehelper.create_connection(self.uri.database(), database_name)
        if not success:
            return False, error_text
        self.database = QSqlDatabase.database(database_name)
        return True, ""

    def select_into_dict_list(self, sql: str, null_value_to_none=True) -> list[dict]:
        result, self.error_text = databasehelper.select_into_dict_list(sql, self.database, null_value_to_none)
        # Unlike PostgreSQL, SQLite has uppercase column names.
        result_lower = [{k.lower(): v for k, v in row.items()} for row in result]
        return result_lower

    def get_column_names(self, table_name: str, force_lower=False) -> list[str]:
        result, self.error_text = sqlitehelper.get_column_names(self.database, table_name, force_lower=force_lower)
        return result

    def get_geom_columns(self, table_name: str, force_lower=False) -> list[str]:
        result, self.error_text = sqlitehelper.get_column_names(self.database, table_name, "FDO_GEOMETRY_as_blob",
                                                                force_lower=force_lower)
        return result

    def get_generic_select_statement(self, table_name: str, column_list=None) -> str:
        if not column_list:
            column_list = self.get_column_names(table_name)

        return f"SELECT {', '.join(column_list)} FROM {table_name}"

    def geom_as_wkt(self, geom_data) -> str:
        # ogr_geom = ogr.CreateGeometryFromWkb(wkb_data)
        # ogr_geom
        #
        #
        # geom = wkb.loads(geom, hex=True)
        # return geom.wkt
        raise NotImplemented("geom_as_wkt not yet implemented")
