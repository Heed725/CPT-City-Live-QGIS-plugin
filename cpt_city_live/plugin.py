"""Activate the bundled archive in QGIS's native CPT-City catalog browser."""
from pathlib import Path
from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsSettings

ARCHIVE_NAME = "cpt-city-new"

class CptCityLivePlugin:
    def __init__(self, iface):
        self.iface, self.action = iface, None
        self.plugin_dir = Path(__file__).parent
        self.archive_parent = self.plugin_dir / "archives"
        self.archive_dir = self.archive_parent / ARCHIVE_NAME

    def initGui(self):
        self.action = QAction(QIcon(str(self.plugin_dir / "icon.svg")), "Activate CPT-City New catalog", self.iface.mainWindow())
        self.action.triggered.connect(self.activate_with_message)
        self.iface.addPluginToRasterMenu("CPT-City Catalog", self.action)
        self.iface.addToolBarIcon(self.action)
        self.activate(show_message=False)

    def activate(self, show_message=True):
        if not self.archive_dir.exists():
            if show_message:
                QMessageBox.critical(self.iface.mainWindow(), "CPT-City Catalog", "The bundled CPT-City archive is missing. Install the plugin from the GitHub Release ZIP, not GitHub's source ZIP.")
            return False
        settings = QgsSettings()
        settings.setValue("CptCity/baseDir", str(self.archive_parent))
        settings.setValue("CptCity/archiveName", ARCHIVE_NAME)
        if show_message:
            QMessageBox.information(self.iface.mainWindow(), "CPT-City New", "The cpt-city-new archive setting has been saved safely.\n\nRestart QGIS to load it. The plugin no longer clears or reloads archives while QGIS is running.")
        return True

    def activate_with_message(self): self.activate(show_message=True)

    def unload(self):
        if self.action:
            self.iface.removePluginRasterMenu("CPT-City Catalog", self.action)
            self.iface.removeToolBarIcon(self.action)
