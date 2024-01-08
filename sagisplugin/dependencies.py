import importlib
import os
import subprocess
import sys

from PyQt5.QtWidgets import QMessageBox
from qgis.core import Qgis
from qgis.utils import iface


def check(required_packages: list[str], path_to_bundled_packages="") -> list[str]:
    """Checks whether the required packages are installed/available.
    Returns list of missing packages.

    :return: List of missing packages.
    """

    missing_packages = []
    for package in required_packages:
        if package in sys.modules or package.lower() in sys.modules:
            continue
        elif importlib.util.find_spec(package) or importlib.util.find_spec(package.lower()):
            continue
        elif path_to_bundled_packages:
            # Add plugin folder to PATH to use included packages if present (plugin folder).
            package_path = os.path.join(path_to_bundled_packages, package)
            if os.path.isdir(package_path):
                sys.path.append(path_to_bundled_packages)
                if importlib.util.find_spec(package):
                    continue
                # Try lowercase
                if importlib.util.find_spec(package.lower()):
                    continue

        missing_packages.append(package)

    return missing_packages


def install(package: str) -> bool:
    try:
        code = subprocess.check_call(["pip", "install", package])
        if code == 0:
            return True
        return False
    except:
        return False


def check_packages(required_packages: list[str], plugin_name="", plugin_path="") -> bool:
    """Checks whether the required packages are installed/available.
    Returns True if all packages are available. If at least one packages is missing, returns false and shows an error.

    :return: False if at least one is missing; otherwise True.
    """

    missing_packages = check(required_packages, plugin_path)

    if not missing_packages:
        return True

    message = "The following software components are required"

    if plugin_name:
        message += " for {}".format(plugin_name)

    message += ":\n\n"
    message += "\n".join(missing_packages)
    message += "\n\n"
    message += "Do you want to install the missing components?"

    dialog = QMessageBox(
        QMessageBox.Question,
        "Missing Dependencies",
        message,
        QMessageBox.Yes | QMessageBox.No
    )
    reply = dialog.exec()

    if reply == QMessageBox.No:
        return False

    error = False
    log = []
    for package in missing_packages:
        success = install(package)
        if success:
            log.append(f"{package} ... " + "Installed")
        else:
            error = True
            log.append(f"{package} ... " + "Installation error")

    if error:
        iface.messageBar().pushMessage(
            plugin_name,
             "Error installing Python packages",
            "\n".join(log),
            level=Qgis.MessageLevel.Critical
        )
    else:
        iface.messageBar().pushMessage(
            plugin_name,
            "Python packages successfully installed",
            "\n".join(log),
            level=Qgis.MessageLevel.Success
        )
        return True
