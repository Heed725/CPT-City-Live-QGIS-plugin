"""Activate the bundled archive in QGIS's native CPT-City catalog browser."""
from pathlib import Path
from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsCptCityArchive, QgsSettings

ARCHIVE_NAME = "cpt-city-full"

class CptCityLivePlugin:
    def __init__(self, iface):
        self.iface, self.action = iface, None
        self.plugin_dir = Path(__file__).parent
        self.archive_parent = self.plugin_dir / "archives"
        self.archive_dir = self.archive_parent / ARCHIVE_NAME

    def initGui(self):
        self.action = QAction(QIcon(str(self.plugin_dir / "icon.svg")), "Activate CPT-City colour catalog", self.iface.mainWindow())
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
        QgsCptCityArchive.clearArchives()
        QgsCptCityArchive.initDefaultArchive()
        archive = QgsCptCityArchive.defaultArchive()
        ok = archive is not None and not archive.isEmpty()
        if show_message:
            if ok:
                QMessageBox.information(self.iface.mainWindow(), "CPT-City Catalog", "CPT-City is active as a QGIS color-ramp catalog.\n\nOpen a color-ramp selector, choose Create New Color Ramp, then select Catalog: cpt-city.")
            else:
                QMessageBox.warning(self.iface.mainWindow(), "CPT-City Catalog", "QGIS could not initialize the bundled catalog. Restart QGIS and activate the plugin again.")
        return ok

    def activate_with_message(self): self.activate(show_message=True)

    def unload(self):
        if self.action:
            self.iface.removePluginRasterMenu("CPT-City Catalog", self.action)
            self.iface.removeToolBarIcon(self.action)
