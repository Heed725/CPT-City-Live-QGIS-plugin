"""CPT-City New: an independent, crash-safe colour-ramp catalog."""
from pathlib import Path

from qgis.PyQt.QtGui import QAction, QIcon

from .browser import CatalogDialog


class CptCityLivePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None
        self.plugin_dir = Path(__file__).parent

    def initGui(self):
        self.action = QAction(QIcon(str(self.plugin_dir / "icon.svg")), "CPT-City New Catalog", self.iface.mainWindow())
        self.action.triggered.connect(self.open_catalog)
        self.iface.addPluginToRasterMenu("CPT-City New", self.action)
        self.iface.addToolBarIcon(self.action)

    def open_catalog(self):
        if self.dialog is None:
            self.dialog = CatalogDialog(self.iface, self.plugin_dir)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def unload(self):
        if self.dialog is not None:
            self.dialog.close()
            self.dialog.deleteLater()
            self.dialog = None
        if self.action:
            self.iface.removePluginRasterMenu("CPT-City New", self.action)
            self.iface.removeToolBarIcon(self.action)

