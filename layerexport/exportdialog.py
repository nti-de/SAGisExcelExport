import os
import pathlib
import re

from PyQt5 import sip
from PyQt5.QtCore import QDateTime, Qt, QDir, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QPushButton, QRadioButton, QButtonGroup, QDialogButtonBox, QGridLayout, \
    QFileDialog, QMenuBar, QWidgetAction, QFrame, QHBoxLayout, QLabel, QSpinBox
from qgis.core import Qgis, QgsProject, QgsVectorLayer
from qgis.utils import iface

from . import excelexport, exportsettings, excelformatting
from .. import loggerutils
from ..gui.twolistselection import TwoListSelection, TwoListSelectionData


class ExportDialog(QDialog):
    """Export dialog."""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/SAGis_Logo_Excel_Export.png")))

        self.layer: QgsVectorLayer = iface.activeLayer()

        self.setStyleSheet("QWidget { font-size: 8pt }")
        self.setWindowTitle("SAGis Excel Export")

        # Field selection
        selected_fields = exportsettings.load_selected_field_ids(self.layer.id())
        self.__item_list = self.get_item_list()
        self.__two_list_selection = TwoListSelection(
            left_list=self.__item_list,
            right_key_list=selected_fields,
            left_caption=self.tr("Fields:"),
            right_caption=self.tr("Fields to export:"),
            clone=True,
            allow_filtering=True
        )
        self.__two_list_selection.filter_by_key = False

        self.__button_export = QPushButton(self.tr("Export"))
        self.__button_export.setDisabled(self.__two_list_selection.right_list_widget.count() == 0)
        self.__two_list_selection.right_count_changed.connect(
            lambda count: self.__button_export.setDisabled(count == 0)
        )

        self.__button_abort = QPushButton(self.tr("Abort"))
        self.__button_abort.setDisabled(True)
        self.__button_abort.clicked.connect(self.abort)

        # Radio buttons
        self.__radio_selected = QRadioButton(self.tr("Only selected features ({})").format(self.layer.selectedFeatureCount()))
        self.__radio_all = QRadioButton(self.tr("All features ({})").format(self.layer.featureCount()))

        # Disable __radio_selected if no features are selected.
        if self.layer.selectedFeatureCount() > 0:
            self.__radio_selected.setEnabled(True)
            self.__radio_selected.setChecked(True)
        else:
            self.__radio_selected.setEnabled(False)
            self.__radio_all.setChecked(True)

        self.__radio_translated = QRadioButton(self.tr("Use displayed values"))
        self.__radio_raw = QRadioButton(self.tr("Use raw field values"))
        self.__radio_translated.setChecked(True)

        # Group radio buttons
        self.__objects_group = QButtonGroup()
        self.__objects_group.addButton(self.__radio_selected)
        self.__objects_group.addButton(self.__radio_all)

        self.__relations_group = QButtonGroup()
        self.__relations_group.addButton(self.__radio_raw)
        self.__relations_group.addButton(self.__radio_translated)

        # Button box
        self.__button_box = QDialogButtonBox()
        self.__button_box.setStandardButtons(QDialogButtonBox.Close)
        self.__button_box.addButton(self.__button_export, QDialogButtonBox.AcceptRole)
        self.__button_box.rejected.connect(self.close)
        self.__button_box.accepted.connect(self.export_clicked)
        self.__button_box.addButton(self.__button_abort, QDialogButtonBox.ActionRole)

        # region Menu bar
        self.__menu_bar = QMenuBar()
        self.__advanced_menu = self.__menu_bar.addMenu(self.tr("&Advanced Settings"))

        # Checkable settings
        self.__prefer_alias_action = self.__advanced_menu.addAction(self.tr("Use &alias"))
        self.__show_index_action = self.__advanced_menu.addAction(self.tr("Show &index"))
        self.__enable_filters_action = self.__advanced_menu.addAction(self.tr("Enable &filters"))
        self.__freeze_row_action = self.__advanced_menu.addAction(self.tr("Freeze &column headers"))

        self.__prefer_alias_action.setCheckable(True)
        self.__show_index_action.setCheckable(True)
        self.__enable_filters_action.setCheckable(True)
        self.__freeze_row_action.setCheckable(True)

        # Freeze columns setting
        self.__freeze_columns_action_widget = QWidgetAction(self.__advanced_menu)
        self.__freeze_columns_frame = QFrame()
        self.__freeze_columns_frame_layout = QHBoxLayout()
        self.__freeze_columns_label = QLabel(self.tr("Freeze left columns:"))
        self.__freeze_columns_max_label = QLabel("(max. 5)")
        self.__freeze_columns_widget = QSpinBox()
        self.__freeze_columns_widget.setMaximum(5)
        self.__freeze_columns_widget.setSpecialValueText(self.tr("None"))
        self.__freeze_columns_frame_layout.addWidget(self.__freeze_columns_label, 0, Qt.AlignLeft)
        self.__freeze_columns_frame_layout.addWidget(self.__freeze_columns_widget, 1, Qt.AlignLeft)
        self.__freeze_columns_frame_layout.addWidget(self.__freeze_columns_max_label, 2, Qt.AlignLeft)
        self.__freeze_columns_frame.setLayout(self.__freeze_columns_frame_layout)
        self.__freeze_columns_action_widget.setDefaultWidget(self.__freeze_columns_frame)
        self.__advanced_menu.addAction(self.__freeze_columns_action_widget)

        # Reset advanced settings
        self.__advanced_menu.addSeparator()
        self.__reset_settings_action = self.__advanced_menu.addAction(self.tr("&Reset advanced settings"))
        self.__reset_settings_action.triggered.connect(self.reset_advanced_settings)
        # endregion

        # region Setup layout
        self.__layout = QGridLayout()
        self.__layout.setMenuBar(self.__menu_bar)
        self.__layout.addWidget(self.__two_list_selection, 0, 0, 1, 2)
        self.__layout.addWidget(self.__radio_selected, 1, 0)
        self.__layout.addWidget(self.__radio_translated, 1, 1)
        self.__layout.addWidget(self.__radio_all, 2, 0)
        self.__layout.addWidget(self.__radio_raw, 2, 1)
        self.__layout.setRowMinimumHeight(3, 20)  # Spacer
        self.__layout.addWidget(self.__button_box, 4, 0, 1, 2)

        # Set layout.
        self.setLayout(self.__layout)

        # Load settings
        self.load_settings()
        self.connect_settings()

        self.file_name = ""
        self.task = None

    def get_item_list(self):
        """Get list of fields that can be exported, excluding fields with hidden widget."""

        item_list = []
        if not self.layer:
            return item_list
        for i, field in enumerate(self.layer.fields()):
            if field.editorWidgetSetup().type() == "Hidden":
                continue
            item_list.append(TwoListSelectionData(i, self.layer.attributeDisplayName(i), field.name()))
        return item_list

    def export_clicked(self):
        """Opens save file dialog and exports data based on the selected options."""

        # Options
        only_selected = self.__radio_selected.isChecked()
        use_converter = self.__radio_translated.isChecked()
        prefer_alias = self.__prefer_alias_action.isChecked()

        # Check if there are features to be exported.
        if self.export_feature_count(only_selected) == 0:
            iface.messageBar().pushInfo("SAGis Excel Export", self.tr("No features to export"))
            return

        default_path = QgsProject.instance().absolutePath()
        layer_name = re.sub(r'[\/:*?"<>|]', "_", self.layer.name())
        default_name = f"{QDateTime.currentDateTime().date().toString('yyyy-MM-dd')}_{layer_name}"

        self.file_name = QFileDialog.getSaveFileName(
            self,
            self.tr("Save as"),
            os.path.join(default_path, default_name),
            self.tr("MS Office Open XML spreadsheet [XLSX] (*.xlsx *.XLSX)")
        )[0]

        if not self.file_name:
            return

        field_ids = list(self.__two_list_selection.get_right_dict().keys())

        exportsettings.save_selected_field_ids(self.layer.id(), list(self.__two_list_selection.get_right_dict().keys()))

        self.task = excelexport.export(self.file_name, self.layer, field_ids, only_selected, use_converter, prefer_alias)
        self.task.taskCompleted.connect(self.on_task_completed)
        self.task.taskTerminated.connect(self.abort)

        self.block_input(True)

    def abort(self):
        if not self.task:
            self.block_input(False)
            return
        if not sip.isdeleted(self.task) and self.task.isActive():
            self.task.cancel()

        if sip.isdeleted(self.task) or not self.task.isActive():
            self.block_input(False)
            self.task = None

    def on_task_completed(self):
        if self.format_file():
            iface.messageBar().pushMessage(
                title=self.tr("Excel Export successful"),
                text=f"<a href='{QUrl.fromLocalFile(str(pathlib.Path(self.file_name).parent)).toString()}'>{QDir.toNativeSeparators(self.file_name)}</a>",
                level=Qgis.MessageLevel.Success,
                duration=0
            )
            self.close()
        else:
            self.block_input(False)

    def format_file(self) -> bool:
        """Formats the created Excel file and closes the dialog if successful."""

        freeze_rows = 1 if exportsettings.freeze_row() else 0
        freeze_panes = (freeze_rows, exportsettings.freeze_columns()) if exportsettings.freeze_row() or exportsettings.freeze_columns() else None

        try:
            excelformatting.format_excel(
                self.file_name,
                index=exportsettings.show_index(),
                freeze_panes=freeze_panes,
                enable_filters=exportsettings.enable_filters()
            )
            return True
        except Exception as e:
            title = self.tr("Excel Export formatting failed")
            message = self.tr("Unformatted/faulty file")
            file_path = f"<a href='{QUrl.fromLocalFile(str(pathlib.Path(self.file_name).parent)).toString()}'>{QDir.toNativeSeparators(self.file_name)}</a>"

            iface.messageBar().pushMessage(title, f"{str(e)}; {message} {file_path}", Qgis.MessageLevel.Warning, 0)

            loggerutils.log_error(
                f"{title}:\n{str(e)}\n\n{message}:\n{QDir.toNativeSeparators(self.file_name)}",
                title=self.tr("Export error")
            )
            return False

    def block_input(self, block: bool):
        self.__button_export.setDisabled(block)
        self.__button_box.button(QDialogButtonBox.StandardButton.Close).setDisabled(block)
        self.__two_list_selection.setDisabled(block)
        self.__radio_all.setDisabled(block)
        self.__radio_selected.setDisabled(block)
        self.__radio_translated.setDisabled(block)
        self.__radio_raw.setDisabled(block)
        self.__menu_bar.setDisabled(block)

        self.__button_abort.setEnabled(block)

    def connect_settings(self):
        self.__prefer_alias_action.triggered.connect(exportsettings.set_prefer_alias)
        self.__show_index_action.triggered.connect(exportsettings.set_show_index)
        self.__enable_filters_action.triggered.connect(exportsettings.set_enable_filters)
        self.__freeze_row_action.triggered.connect(exportsettings.set_freeze_row)
        self.__freeze_columns_widget.valueChanged.connect(exportsettings.set_freeze_columns)

    def load_settings(self):
        self.__prefer_alias_action.setChecked(exportsettings.prefer_alias())
        self.__show_index_action.setChecked(exportsettings.show_index())
        self.__enable_filters_action.setChecked(exportsettings.enable_filters())
        self.__freeze_row_action.setChecked(exportsettings.freeze_row())
        self.__freeze_columns_widget.setValue(exportsettings.freeze_columns())

    def reset_advanced_settings(self):
        if not self.__prefer_alias_action.isChecked():
            self.__prefer_alias_action.trigger()

        if self.__show_index_action.isChecked():
            self.__show_index_action.trigger()

        if self.__enable_filters_action.isChecked():
            self.__enable_filters_action.trigger()

        if self.__freeze_row_action.isChecked():
            self.__freeze_row_action.trigger()

        self.__freeze_columns_widget.setValue(0)

    def export_feature_count(self, only_selected: bool) -> int:
        if only_selected:
            return self.layer.selectedFeatureCount()
        return self.layer.featureCount()
