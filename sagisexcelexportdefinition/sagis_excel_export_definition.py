from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SagisWorksheetType:
    class Meta:
        name = "SAGisWorksheetType"

    access_right: Optional[str] = field(
        default=None,
        metadata={
            "name": "AccessRight",
            "type": "Element",
            "required": True,
            "min_length": 0,
            "max_length": 255,
        }
    )
    tab_color: Optional[str] = field(
        default=None,
        metadata={
            "name": "TabColor",
            "type": "Element",
            "required": True,
            "min_length": 0,
            "max_length": 255,
        }
    )
    work_sheet_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "WorkSheetName",
            "type": "Element",
            "required": True,
            "min_length": 0,
            "max_length": 255,
        }
    )
    column_header_aliases: Optional["SagisWorksheetType.ColumnHeaderAliases"] = field(
        default=None,
        metadata={
            "name": "ColumnHeaderAliases",
            "type": "Element",
        }
    )
    provider_type_restrictions: Optional["SagisWorksheetType.ProviderTypeRestrictions"] = field(
        default=None,
        metadata={
            "name": "ProviderTypeRestrictions",
            "type": "Element",
        }
    )
    sql: Optional[str] = field(
        default=None,
        metadata={
            "name": "Sql",
            "type": "Element",
            "required": True,
            "min_length": 1,
            "max_length": 65536,
        }
    )
    without_selection: bool = field(
        default=False,
        metadata={
            "name": "WithoutSelection",
            "type": "Element",
        }
    )
    active: bool = field(
        default=True,
        metadata={
            "name": "Active",
            "type": "Element",
        }
    )
    order_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrderBy",
            "type": "Element",
            "min_length": 1,
            "max_length": 65536,
        }
    )

    @dataclass
    class ColumnHeaderAliases:
        alias: List["SagisWorksheetType.ColumnHeaderAliases.Alias"] = field(
            default_factory=list,
            metadata={
                "name": "Alias",
                "type": "Element",
            }
        )

        @dataclass
        class Alias:
            value: str = field(
                default="",
                metadata={
                    "required": True,
                }
            )
            column_name: Optional[str] = field(
                default=None,
                metadata={
                    "name": "ColumnName",
                    "type": "Attribute",
                    "required": True,
                }
            )
            title: Optional[str] = field(
                default=None,
                metadata={
                    "name": "Title",
                    "type": "Attribute",
                }
            )

    @dataclass
    class ProviderTypeRestrictions:
        type: List[str] = field(
            default_factory=list,
            metadata={
                "name": "Type",
                "type": "Element",
            }
        )


@dataclass
class SagisExcelExportItemType:
    class Meta:
        name = "SAGisExcelExportItemType"

    feature_class: Optional[str] = field(
        default=None,
        metadata={
            "name": "FeatureClass",
            "type": "Element",
            "required": True,
            "min_length": 1,
            "max_length": 255,
        }
    )
    title: Optional[str] = field(
        default=None,
        metadata={
            "name": "Title",
            "type": "Element",
            "required": True,
            "min_length": 1,
            "max_length": 255,
        }
    )
    file_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileName",
            "type": "Element",
            "min_length": 1,
            "max_length": 255,
        }
    )
    provider_type_restrictions: Optional["SagisExcelExportItemType.ProviderTypeRestrictions"] = field(
        default=None,
        metadata={
            "name": "ProviderTypeRestrictions",
            "type": "Element",
        }
    )
    project_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ProjectId",
            "type": "Element",
        }
    )
    work_sheet: List[SagisWorksheetType] = field(
        default_factory=list,
        metadata={
            "name": "WorkSheet",
            "type": "Element",
            "min_occurs": 1,
        }
    )

    @dataclass
    class ProviderTypeRestrictions:
        type: List[str] = field(
            default_factory=list,
            metadata={
                "name": "Type",
                "type": "Element",
            }
        )


@dataclass
class SagisExcelExportDefinitionType:
    class Meta:
        name = "SAGisExcelExportDefinitionType"

    sagis_excel_export_item: Optional[SagisExcelExportItemType] = field(
        default=None,
        metadata={
            "name": "SAGisExcelExportItem",
            "type": "Element",
        }
    )


@dataclass
class SagisExcelExportDefinition(SagisExcelExportDefinitionType):
    class Meta:
        name = "SAGisExcelExportDefinition"
