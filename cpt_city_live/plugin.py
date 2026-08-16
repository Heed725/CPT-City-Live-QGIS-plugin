"""Offline, one-click installer for bundled cpt-city QGIS ramps."""
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from qgis.PyQt.QtCore import QSettings, QThread, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QAction, QColor, QIcon
from qgis.PyQt.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QProgressBar, QPushButton, QVBoxLayout
from qgis.core import QgsGradientColorRamp, QgsGradientStop, QgsStyle

BATCH_SIZE = 25

def rgba(value):
    bits = [int(float(x)) for x in value.split(",")[:4]]
    while len(bits) < 4: bits.append(255)
    return QColor(*bits)

def ramp_from_record(record):
    props, stops = record["props"], []
    for token in props.get("stops", "").split(":") if props.get("stops") else []:
        if ";" not in token: continue
        offset, color = token.split(";", 1)
        try: stops.append(QgsGradientStop(float(offset), rgba(color)))
        except (TypeError, ValueError): pass
    return QgsGradientColorRamp(rgba(props.get("color1", "0,0,0,255")), rgba(props.get("color2", "255,255,255,255")), props.get("discrete", "0") == "1", stops)

class BundleLoader(QThread):
    loaded, failed = pyqtSignal(object), pyqtSignal(str)
    def __init__(self, xml_path, parent=None): super().__init__(parent); self.xml_path = xml_path
    def run(self):
        try:
            records = []
            for _, element in ET.iterparse(self.xml_path, events=("end",)):
                if element.tag != "colorramp": continue
                records.append({"name": element.get("name", "cpt-city/unnamed"), "props": {p.get("k", ""): p.get("v", "") for p in element.findall("prop")}})
                element.clear()
            self.loaded.emit(records)
        except Exception as error: self.failed.emit(str(error))

class InstallerDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir, self.xml_path = plugin_dir, plugin_dir / "palettes.xml"
        try: self.manifest = json.loads((plugin_dir / "bundle.json").read_text(encoding="utf-8"))
        except Exception: self.manifest = {}
        count, version = self.manifest.get("palette_count", 0), self.manifest.get("cpt_city_version", "unknown")
        self.records, self.position, self.installed, self.loader = [], 0, 0, None
        self.setWindowTitle("CPT-City Offline Palette Installer"); self.resize(610, 260)
        layout = QVBoxLayout(self)
        description = QLabel(f"This plugin already contains <b>{count:,}</b> QGIS colour ramps from cpt-city {version}. No catalogue download is required.")
        description.setWordWrap(True)
        self.status = QLabel("Click Install to add the bundled ramps to QGIS Style Manager."); self.status.setWordWrap(True)
        self.progress = QProgressBar(); self.progress.setRange(0, max(count, 1)); self.progress.setValue(0)
        layout.addWidget(QLabel("<h2>Install CPT-City colour ramps in QGIS</h2>")); layout.addWidget(description); layout.addWidget(self.status); layout.addWidget(self.progress)
        buttons = QHBoxLayout(); buttons.addStretch(1)
        self.install_button, self.close_button = QPushButton(f"Install {count:,} palettes"), QPushButton("Close")
        buttons.addWidget(self.install_button); buttons.addWidget(self.close_button); layout.addLayout(buttons)
        self.install_button.clicked.connect(self.start_install); self.close_button.clicked.connect(self.accept)
        if not self.xml_path.exists() or not count:
            self.install_button.setEnabled(False)
            self.status.setText("Bundled palette XML is missing. Install the plugin from the GitHub Release ZIP, not GitHub's source ZIP.")

    def start_install(self):
        self.install_button.setEnabled(False); self.close_button.setEnabled(False); self.status.setText("Reading bundled QGIS XML colours…")
        self.loader = BundleLoader(str(self.xml_path), self); self.loader.loaded.connect(self.begin_batches); self.loader.failed.connect(self.load_failed); self.loader.start()

    def begin_batches(self, records):
        self.records, self.position, self.installed = records, 0, 0
        self.progress.setRange(0, max(len(records), 1)); self.status.setText("Installing colour ramps into QGIS Style Manager…"); QTimer.singleShot(0, self.install_batch)

    def install_batch(self):
        style, end = QgsStyle.defaultStyle(), min(self.position + BATCH_SIZE, len(self.records))
        for record in self.records[self.position:end]:
            if style.addColorRamp(record["name"], ramp_from_record(record), True): self.installed += 1
        self.position = end; self.progress.setValue(end); self.status.setText(f"Installing {end:,} of {len(self.records):,} palettes…")
        if end < len(self.records): QTimer.singleShot(0, self.install_batch)
        else:
            style.save(); QSettings().setValue("cptCityOffline/installedVersion", self.manifest.get("cpt_city_version", ""))
            self.status.setText(f"Complete — {self.installed:,} colour ramps are ready in QGIS Style Manager.")
            self.close_button.setEnabled(True); self.install_button.setText("Reinstall palettes"); self.install_button.setEnabled(True)
            QMessageBox.information(self, "CPT-City Offline", "Installation complete. Search for cpt-city/ in any QGIS colour-ramp selector.")

    def load_failed(self, error):
        self.close_button.setEnabled(True); self.install_button.setEnabled(True); QMessageBox.critical(self, "CPT-City Offline", f"Could not read the bundled palette XML:\n\n{error}")

class CptCityLivePlugin:
    def __init__(self, iface): self.iface, self.action, self.dialog, self.plugin_dir = iface, None, None, Path(__file__).parent
    def initGui(self):
        self.action = QAction(QIcon(str(self.plugin_dir / "icon.svg")), "Install CPT-City palettes", self.iface.mainWindow()); self.action.triggered.connect(self.run)
        self.iface.addPluginToRasterMenu("CPT-City Offline", self.action); self.iface.addToolBarIcon(self.action)
    def unload(self):
        if self.action: self.iface.removePluginRasterMenu("CPT-City Offline", self.action); self.iface.removeToolBarIcon(self.action)
    def run(self):
        self.dialog = InstallerDialog(self.plugin_dir, self.iface.mainWindow()); self.dialog.show(); self.dialog.raise_(); self.dialog.activateWindow()
