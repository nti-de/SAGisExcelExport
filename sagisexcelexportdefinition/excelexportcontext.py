from dataclasses import dataclass

from .sagis_excel_export_definition import SagisExcelExportDefinition
from ..datasources.datasource import DataSource


@dataclass
class ExcelExportContext:
    config: SagisExcelExportDefinition
    datasource: DataSource
    primary_key_name: str
    object_ids: list[int]
    file_path: str
