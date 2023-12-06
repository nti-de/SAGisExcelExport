from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QToolBar


class SagisPluginBase:
    """Base class for SAGis plugins for QGIS."""

    def __init__(self, iface, plugin_name: str, menu_text: str):
        self.iface = iface
        self.plugin_name = plugin_name
        self.plugin_menu_text = menu_text

        self.actions: list[QAction] = []

        # Use existing SAGis menu if possible
        self.sagis_menu = self.iface.mainWindow().findChild(QMenu, "sagis_menu")
        if not self.sagis_menu:
            self.sagis_menu = QMenu('&SAGis', self.iface.mainWindow().menuBar())
            actions = self.iface.mainWindow().menuBar().actions()
            self.iface.mainWindow().menuBar().insertMenu(actions[-2], self.sagis_menu)
            self.sagis_menu.setObjectName("sagis_menu")

        self.menu = self.sagis_menu.addMenu(self.plugin_menu_text)

        # Use existing SAGis toolbar if possible
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, "sagis_toolbar")

    def add_action(
            self,
            text,
            callback,
            icon_path=None,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        if icon_path is not None:
            icon = QIcon(icon_path)
            action = QAction(icon, text, parent)
        else:
            action = QAction(text, parent)

        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            if not self.toolbar:
                self.add_tool_bar()
            self.toolbar.addAction(action)

        if add_to_menu:
            self.menu.addAction(action)

        self.actions.append(action)

        return action

    def add_tool_bar(self):
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar("SAGis Toolbar")
            self.toolbar.setToolTip("SAGis Tools")
            self.toolbar.setObjectName("sagis_toolbar")

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            if self.toolbar:
                self.toolbar.removeAction(action)
            if self.menu:
                self.menu.removeAction(action)

        if self.sagis_menu:
            self.sagis_menu.removeAction(self.menu.menuAction())
            if self.sagis_menu.isEmpty():
                self.sagis_menu.deleteLater()

        if self.toolbar and not self.toolbar.actions():
            del self.toolbar
