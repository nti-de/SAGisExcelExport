import os.path

from PyQt5.QtWidgets import QMenu, QToolButton

from . import PLUGIN_NAME
from .datasources import datasourcefactory
from .layerexport.exportdialog import ExportDialog
from .sagisexcelexportdefinition.exceltemplateexportdialog import ExcelTemplateExportDialog
from .sagisplugin.sagispluginbase import SagisPluginBase


class SagisExcelExportPlugin(SagisPluginBase):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        super().__init__(
            iface,
            PLUGIN_NAME,
            "Excel Export"
        )

        # Declare instance attributes
        self.sagis_icon = os.path.abspath(os.path.join(self.plugin_dir, "resources/SAGis_Logo_Excel_Export.png"))
        self.tool_button = None
        self.popup_menu = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        export_action = self.add_action(
            text="Excel Export...",
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
            icon_path=self.sagis_icon,
        )

        export_with_template_action = self.add_action(
            text="Export mit Vorlage (PostgreSQL)...",
            callback=self.export_with_template,
            add_to_toolbar=False,
            parent=self.iface.mainWindow()
        )

        self.popup_menu = QMenu()
        self.popup_menu.addAction(export_with_template_action)

        self.tool_button = QToolButton()
        self.tool_button.setDefaultAction(export_action)
        self.tool_button.setMenu(self.popup_menu)
        self.tool_button.setPopupMode(QToolButton.MenuButtonPopup)

        if not self.toolbar:
            self.add_tool_bar()
        self.actions.append(self.toolbar.addWidget(self.tool_button))

    def run(self):
        """Run method that performs all the real work"""

        if not self.iface.activeLayer():
            self.iface.messageBar().pushInfo("SAGis Excel Export", "Kein Layer ausgewählt")
            return

        dlg = ExportDialog()
        dlg.setModal(True)
        dlg.show()
        dlg.exec_()

    def export_with_template(self):
        """Excel export with templates"""

        layer = self.iface.activeLayer()
        if not layer:
            self.iface.messageBar().pushInfo("SAGis Excel Export", "Kein Layer ausgewählt")
            return

        class_name = layer.dataProvider().uri().table()
        if not class_name:
            self.iface.messageBar().pushInfo("SAGis Excel Export", f"Keine Tabelle für Layer '{layer.name()} angegeben'")
            return

        pk_attributes = layer.primaryKeyAttributes()
        if not pk_attributes:
            self.iface.messageBar().pushInfo("SAGis Excel Export", f"Kein Primärschlüssel für Layer '{layer.name()}'")
            return
        pk_name = layer.fields().field(pk_attributes[0]).name()

        datasource = datasourcefactory.create_datasource_from_data_provider(layer.dataProvider())
        if not datasource or not datasource.connection_success:
            self.iface.messageBar().pushInfo("SAGis Excel Export", "Es konnte keine Datenquelle konfiguriert werden")
            return

        dlg = ExcelTemplateExportDialog(
            class_name=class_name,
            datasource=datasource,
            primary_key_name=pk_name,
            parent=self.iface.mainWindow()
        )
        dlg.setModal(True)
        dlg.show()
        dlg.exec_()
