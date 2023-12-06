from typing import Optional

from qgis._core import QgsVectorDataProvider
from qgis.core import QgsDataProvider

from .datasource import DataSource
from .postgresdatasource import PostgresDataSource
from .sqlitedatasource import SqliteDataSource


def create_datasource_from_data_provider(provider: QgsDataProvider) -> Optional[DataSource]:
    if not provider or not provider.uri():
        return None

    if provider.name() == "postgres" and provider.storageType() == "PostgreSQL database with PostGIS extension":
        return PostgresDataSource(provider.uri())

    if provider.name() == "ogr" and provider.storageType() == "SQLite":
        return SqliteDataSource(provider.uri())

    else:
        return None
