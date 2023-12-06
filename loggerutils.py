from logging import Logger

from PyQt5.QtWidgets import QDockWidget
from qgis.gui import QgsMessageViewer
from qgis.core import Qgis, QgsMessageLog
from qgis.utils import iface

TAG = "SAGis Excel Export"


def log_warning(message: str, title="", show_message_log=False, logger_: Logger = None) -> None:
    QgsMessageLog.logMessage(message=message, tag=TAG, level=Qgis.MessageLevel.Warning, notifyUser=True)
    show_message_viewer(message, title=title)

    if show_message_log:
        open_message_log()

    if isinstance(logger_, Logger):
        logger_.warning(message)


def log_error(message: str, title="", show_message_log=False, logger_: Logger = None) -> None:
    QgsMessageLog.logMessage(message=message, tag=TAG, level=Qgis.MessageLevel.Critical, notifyUser=True)
    show_message_viewer(message, title=title)

    if show_message_log:
        open_message_log()

    if isinstance(logger_, Logger):
        logger_.error(message)


def log_info(message: str, title="", show_message_log=False, logger_: Logger = None) -> None:
    show_info(message)
    show_message_viewer(message, title=title)

    if show_message_log:
        open_message_log()

    if isinstance(logger_, Logger):
        logger_.info(message)


def show_info(message: str) -> None:
    QgsMessageLog.logMessage(message=message, tag=TAG, level=Qgis.MessageLevel.Info, notifyUser=True)


def show_message_viewer(message: str, title="") -> None:
    message_viewer = QgsMessageViewer()
    message_viewer.setTitle(title or TAG)  # Use TAG as default.
    message_viewer.setMessageAsPlainText(message)
    message_viewer.showMessage()


def open_message_log() -> None:
    widget = iface.mainWindow().findChild(QDockWidget, "MessageLog")
    if widget:
        widget.show()
