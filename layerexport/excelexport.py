import pathlib
import re

from PyQt5.QtCore import QUrl, QDir
from qgis.core import Qgis, QgsTask, QgsApplication, QgsVectorFileWriter, QgsVectorFileWriterTask, QgsVectorLayer
from qgis.utils import iface

from .. import loggerutils
from .customfieldvalueconverter import CustomFieldValueConverter


def export(file_name: str, layer: QgsVectorLayer = None, field_ids=list[int], only_selected=False, use_converter=True, prefer_alias=True) -> QgsTask:
    """Default layer is the active one."""

    if not layer:
        layer = iface.activeLayer()

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.layerName = re.sub(r'[\/:*?"]', "_", layer.name())[:31]
    options.driverName = "XLSX"
    options.fileEncoding = "utf-8"
    options.onlySelectedFeatures = only_selected
    if prefer_alias:
        options.fieldNameSource = QgsVectorFileWriter.FieldNameSource.PreferAlias
    if isinstance(field_ids, list) and len(field_ids) > 0:
        options.attributes = field_ids

    if use_converter:
        converter = CustomFieldValueConverter(layer, prefer_alias)
        options.fieldValueConverter = converter

    task = QgsVectorFileWriterTask(layer, file_name, options)
    # task.taskCompleted.connect(lambda: on_success(file_name))
    task.errorOccurred.connect(lambda error, error_message: on_failure(error, error_message, file_name))
    QgsApplication.taskManager().addTask(task)

    return task


def on_failure(error, error_message, file_name):
    if error == QgsVectorFileWriter.Canceled:
        iface.messageBar().pushMessage(
            "Export abgebrochen",
            f"Daten teilweise exportiert nach <a href='{QUrl.fromLocalFile(str(pathlib.Path(file_name).parent)).toString()}'>{QDir.toNativeSeparators(file_name)}</a>",
            Qgis.MessageLevel.Info,
            0
        )
        return

    # Not canceled by the user.
    loggerutils.log_error(f"Export fehlgeschlagen:\n{error_message}", title="Exportfehler")
