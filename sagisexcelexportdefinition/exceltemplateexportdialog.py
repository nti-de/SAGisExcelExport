import glob
import os
import pathlib

from PyQt5.QtCore import QUrl, QDir, Qt
from PyQt5.QtGui import QStandardItem, QIcon
from qgis.core import Qgis, QgsApplication, QgsProject, QgsTask, QgsVectorLayer
from qgis.utils import iface

from .excelexporttask import ExcelExportTask
from .. import loggerutils
from ..datasources.datasource import DataSource
from ..sagisexcelexportdefinition.sagis_excel_export_definition import *
from ..sagisexcelexportdefinition.excelexportcontext import ExcelExportContext
from ..gui.twolistselection import TwoListSelection

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QRadioButton, QButtonGroup, QPushButton, \
    QFileDialog, QWidget


class ExcelTemplateExportDialog(QDialog):
    CONFIG_PATH = "resources/config/Export"

    def __init__(self, class_name: str, datasource: DataSource, primary_key_name: str, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/SAGis_Logo_Excel_Export.png")))

        self.class_name = class_name

        self.layer: QgsVectorLayer = iface.activeLayer()

        self.selected_object_ids = [{primary_key_name: f.attribute(primary_key_name)} for f in self.layer.selectedFeatures()]

        self.datasource = datasource
        self.primary_key_name = primary_key_name
        self.column_names = self.get_column_names()

        self.setStyleSheet("QWidget { font-size: 8pt }")
        self.setWindowTitle("SAGis Excel Export")

        # Reports
        self.label_reports = QLabel(self.tr("Export template"))
        self.label_reports.setFixedHeight(13)
        self.combo_box_reports = QComboBox()

        # Columns
        self.two_list_selection = TwoListSelection(
            left_list=sorted(self.column_names, key=str.casefold),
            left_caption=self.tr("Fields:"),
            right_caption=self.tr("Fields to export:"),
            clone=True,
            allow_filtering=True
        )
        self.two_list_selection.right_list_changed.connect(self.populate_sort_order)

        # Sort order
        self.label_sort_order = QLabel(self.tr("Sorting order"))
        self.label_sort_order.setFixedHeight(13)
        self.combo_box_sort_order = QComboBox()
        self.populate_sort_order(self.two_list_selection.get_right_dict())

        # Current or all
        self.radio_button_current = QRadioButton(self.tr("Only selected features ({})").format(self.layer.selectedFeatureCount()))
        self.radio_button_all = QRadioButton(self.tr("All features ({})").format(self.layer.featureCount()))
        self.button_create = QPushButton(self.tr("Export"))
        self.button_close = QPushButton(self.tr("Close"))

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.radio_button_current)
        self.button_group.addButton(self.radio_button_all)

        # Disable radio_button_current if no features are selected.
        if self.layer.selectedFeatureCount() > 0:
            self.radio_button_current.setEnabled(True)
            self.radio_button_current.setChecked(True)
        else:
            self.radio_button_current.setEnabled(False)
            self.radio_button_all.setChecked(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.label_reports)
        self.layout().addWidget(self.combo_box_reports)
        self.layout().addWidget(self.two_list_selection)
        self.layout().addWidget(self.label_sort_order)
        self.layout().addWidget(self.combo_box_sort_order)
        self.layout().addWidget(self.radio_button_current)
        self.layout().addWidget(self.radio_button_all)
        self.layout().addWidget(self.button_create)
        self.layout().addWidget(self.button_close)

        # Let added widgets keep their height
        self.filler_widget = QWidget()
        self.layout().addWidget(self.filler_widget)

        self.combo_box_reports.currentIndexChanged.connect(self.selected_report_changed)
        self.button_close.clicked.connect(self.close)
        self.button_create.clicked.connect(self.button_create_clicked)

        self.configs = []

        if not self.read_configs():
            self.close()
        self.populate_reports()

        self.file_path = ""
        self.task: Optional[ExcelExportTask] = None

    def read_configs(self) -> bool:
        """Reads config files. Returns True if no error occurred, False otherwise.

        :return: True if no error occurred, False otherwise.
        """

        # Import XmlParser
        from xsdata.formats.dataclass.parsers import XmlParser

        # Included configs
        try:
            directory = os.path.join(pathlib.Path(__file__).parent.parent, pathlib.Path(self.CONFIG_PATH).__str__(), "*.xml")
            file_list = glob.glob(directory)
        except Exception as e:
            loggerutils.log_error(self.tr("Error reading configuration files:\n{}").format(str(e)))
            return False

        # Custom configs, only works if the project file exists
        try:
            project_path = QgsProject.instance().absolutePath()
            if project_path:
                directory = os.path.join(project_path, pathlib.Path(self.CONFIG_PATH).__str__(), "*.xml")
                custom_list = glob.glob(directory)
                file_list.extend(custom_list)
        except Exception as e:
            loggerutils.log_error(self.tr("Error reading configuration files:\n{}").format(str(e)))
            return False

        # Parse configs
        for file in file_list:
            try:
                xml = pathlib.Path(file).read_text()
                parser = XmlParser()
                config = parser.from_string(xml, SagisExcelExportDefinition)
                if config.sagis_excel_export_item.feature_class.lower() == self.class_name.lower():
                    # Skip if provider restriction is set but not satisfied.
                    if config.sagis_excel_export_item.provider_type_restrictions\
                        and config.sagis_excel_export_item.provider_type_restrictions.type\
                        and self.datasource.feature_source_provider_type.lower()\
                            not in [t.lower() for t in config.sagis_excel_export_item.provider_type_restrictions.type]:
                        continue

                    self.configs.append(config)
            except Exception as e:
                loggerutils.log_error(self.tr("Error reading configuration file\n'{}':\n{}").format(file, str(e)))
                return False

        return True

    def populate_reports(self):
        self.combo_box_reports.clear()
        for config in self.configs:
            self.combo_box_reports.addItem(config.sagis_excel_export_item.title, config)

        report_count = self.combo_box_reports.count()
        if report_count > 0:
            self.combo_box_reports.addItem("_" * 50)
            item: QStandardItem = self.combo_box_reports.model().item(report_count)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        self.combo_box_reports.addItem(self.tr("Data export - Entire data set"), -1)

    def populate_sort_order(self, items: dict):
        self.combo_box_sort_order.clear()
        self.combo_box_sort_order.addItem("")
        if items:
            self.combo_box_sort_order.addItems(sorted(list(items.keys())))
        else:
            self.combo_box_sort_order.addItems(sorted(self.column_names))

    def selected_report_changed(self, _: int):
        report = self.combo_box_reports.currentData()

        self.two_list_selection.setVisible(report == -1)
        self.label_sort_order.setVisible(report == -1)
        self.combo_box_sort_order.setVisible(report == -1)

        if self.two_list_selection.isVisible():
            self.resize(max(self.width(), 732), max(self.height(), 515))

    def get_column_names(self) -> list[str]:
        column_names = self.datasource.get_column_names(self.class_name.lower())
        return column_names

    def button_create_clicked(self):
        if self.task and self.task.status() == QgsTask.TaskStatus.Running:
            self.task.cancel()
        else:
            # Check if there are features to be exported.
            if self.export_feature_count() == 0:
                iface.messageBar().pushInfo("SAGis Excel Export", self.tr("No features to export"))
                return

            config = self.combo_box_reports.currentData()
            if not config:
                return
            if isinstance(config, SagisExcelExportDefinition):
                self.create_export_with_config(config)
            elif config == -1:
                self.create_generic_export()

    def get_save_file_name(self, default_name: str):
        default_path = QgsProject.instance().absolutePath() or os.getcwd()
        self.file_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save as"),
            os.path.join(default_path, default_name),
            self.tr("MS Office Open XML spreadsheet [XLSX] (*.xlsx *.XLSX)")
        )[0]

    def create_export_with_config(self, config: SagisExcelExportDefinition):
        default_name = config.sagis_excel_export_item.file_name or config.sagis_excel_export_item.feature_class
        self.get_save_file_name(default_name)
        if not self.file_path:
            return

        if self.radio_button_current.isChecked():
            features = self.layer.selectedFeatures()
        else:
            features = self.layer.getFeatures()

        ids = [f.attribute(self.primary_key_name) for f in features]

        if not ids:
            iface.messageBar().pushInfo("SAGis Excel Export", self.tr("No feature ids to export"))
            return

        context = ExcelExportContext(
            config=config,
            datasource=self.datasource,
            primary_key_name=self.primary_key_name,
            object_ids=ids,
            file_path=self.file_path
        )

        self.task = ExcelExportTask(context)
        self.task.taskCompleted.connect(self.task_completed)
        self.task.taskTerminated.connect(self.task_completed)
        QgsApplication.taskManager().addTask(self.task)

        self.button_create.setText(self.tr("Abort"))
        self.button_close.setDisabled(True)

    def create_generic_export(self):
        """Builds and uses SagisExcelExportDefinition."""

        selected_columns = (self.two_list_selection.get_right_dict().keys())
        sql = self.datasource.get_generic_select_statement(self.class_name, selected_columns)
        sql += f" WHERE {self.primary_key_name} = {{0}}"

        order_column = self.combo_box_sort_order.currentText()

        worksheet = SagisWorksheetType(
            tab_color="blue",
            work_sheet_name=self.tr("Worksheet Export"),
            sql=sql,
            order_by=order_column if order_column else None
        )

        export_item = SagisExcelExportItemType(
            feature_class=self.class_name.lower(),
            work_sheet=[worksheet]
        )

        config = SagisExcelExportDefinition(sagis_excel_export_item=export_item)
        self.create_export_with_config(config)

    def task_completed(self):
        if self.task.status() == QgsTask.TaskStatus.Complete:
            iface.messageBar().pushMessage(
                title=self.tr("Excel Export successful"),
                text=f"<a href='{QUrl.fromLocalFile(str(pathlib.Path(self.file_path).parent)).toString()}'>{QDir.toNativeSeparators(self.file_path)}</a>",
                level=Qgis.MessageLevel.Success,
                duration=0
            )
        elif self.task.error:
            loggerutils.log_error(
                self.tr("Export failed:\n{}").format(str(self.task.error)),
                title=self.tr("Export error")
            )

        self.task = None
        self.button_create.setText(self.tr("Export"))
        self.button_close.setEnabled(True)

    def export_feature_count(self) -> int:
        if self.radio_button_current.isChecked():
            return self.layer.selectedFeatureCount()
        return self.layer.featureCount()
