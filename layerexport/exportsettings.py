from pathlib import Path
from typing import Any
from qgis.core import QgsProject, QgsSettings

SAGIS_EXCEL_EXPORT_PATH = "SAGis/SAGisExcelExport"


def save_setting(key, value):
    settings = QgsSettings()
    setting_key = f"{SAGIS_EXCEL_EXPORT_PATH}/settings/{key}"
    if value is not None:
        settings.setValue(setting_key, value)
    else:
        settings.remove(setting_key)


def load_setting(key, type_: type, default_value=None) -> Any:
    settings = QgsSettings()
    setting_key = f"{SAGIS_EXCEL_EXPORT_PATH}/settings/{key}"
    return settings.value(setting_key, default_value, type_)


def save_selected_field_ids(layer_id: str, field_ids: list[int]):
    settings = QgsSettings()
    project_name = Path(QgsProject.instance().fileName()).stem
    setting_key = f"{SAGIS_EXCEL_EXPORT_PATH}/selected_fields/{project_name}/{layer_id}"
    if field_ids:
        settings.setValue(setting_key, field_ids)
    else:
        settings.remove(setting_key)


def load_selected_field_ids(layer_id: str) -> list[int]:
    settings = QgsSettings()
    project_name = Path(QgsProject.instance().fileName()).stem
    setting_key = f"{SAGIS_EXCEL_EXPORT_PATH}/selected_fields/{project_name}/{layer_id}"
    return settings.value(setting_key, [], int)


def prefer_alias() -> bool:
    return load_setting("prefer_alias", bool, True)


def show_index() -> bool:
    return load_setting("show_index", bool, False)


def enable_filters() -> bool:
    return load_setting("enable_filters", bool, False)


def freeze_row() -> bool:
    return load_setting("freeze_row", bool, False)


def freeze_columns() -> int:
    return load_setting("freeze_columns", int, 0)


def set_prefer_alias(value: bool) -> None:
    save_setting("prefer_alias", value)


def set_show_index(value: bool) -> None:
    save_setting("show_index", value)


def set_enable_filters(value: bool) -> None:
    save_setting("enable_filters", value)


def set_freeze_row(value: bool) -> None:
    save_setting("freeze_row", value)


def set_freeze_columns(value: int) -> None:
    save_setting("freeze_columns", value)
