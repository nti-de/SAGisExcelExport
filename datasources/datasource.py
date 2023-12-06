from abc import ABC, abstractmethod
from typing import Optional, Tuple

from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsDataSourceUri

from .featuresourceprovidertype import FeatureSourceProviderType


class DataSource(ABC):
    PROJECT_ENTRY_SCOPE = "sagis_alkis_search"

    def __init__(self, uri: QgsDataSourceUri):
        self.uri = uri
        self.database: Optional[QSqlDatabase] = None
        self.connection_success, self.error_text = self.create_connection()

        self.feature_source_provider_type: FeatureSourceProviderType = FeatureSourceProviderType.Unknown

    def close_and_remove_connection(self):
        if self.database:
            self.database.close()
            QSqlDatabase.removeDatabase(self.database.connectionName())

    @abstractmethod
    def create_connection(self) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def select_into_dict_list(self, sql: str, null_value_to_none=True) -> list[dict]:
        pass

    @abstractmethod
    def get_column_names(self, table_name: str, force_lower=False) -> list[str]:
        pass

    @abstractmethod
    def get_geom_columns(self, table_name: str, force_lower=False) -> list[str]:
        pass

    @abstractmethod
    def get_generic_select_statement(self, table_name: str, column_list=None) -> str:
        pass
