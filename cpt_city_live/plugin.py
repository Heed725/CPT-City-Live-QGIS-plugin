from pathlib import Path

from qgis.PyQt.QtCore import Qt, QSettings, QSize
from qgis.PyQt.QtGui import QAction, QColor, QIcon, QLinearGradient, QPainter, QPixmap
from qgis.PyQt.QtWidgets import (QAbstractItemView, QCheckBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QProgressBar,
    QPushButton, QVBoxLayout)
from qgis.core import QgsApplication, QgsGradientColorRamp, QgsGradientStop, QgsStyle
from .core import load_local_index, sync_catalogue

def rgba(value):
    bits = [int(float(x)) for x in value.split(",")[:4]]
    while len(bits) < 4: bits.append(255)
    return QColor(*bits)

def ramp_from_palette(palette):
    stops = []
    for token in palette.stops.split(":") if palette.stops else []:
        if ";" not in token: continue
        offset, color = token.split(";", 1)
        try: stops.append(QgsGradientStop(float(offset), rgba(color)))
        except (TypeError, ValueError): pass
    return QgsGradientColorRamp(rgba(palette.color1), rgba(palette.color2), palette.discrete, stops)

def preview_icon(palette, width=260, height=28):
    pixmap = QPixmap(width, height)
    gradient = QLinearGradient(0, 0, width, 0)
    ramp = ramp_from_palette(palette)
    for i in range(81):
        x = i / 80.0
        gradient.setColorAt(x, ramp.color(x))
    painter = QPainter(pixmap)
    painter.fillRect(pixmap.rect(), gradient)
    painter.end()
    return QIcon(pixmap)

class PaletteDialog(QDialog):
    def __init__(self, data_dir, parent=None):
        super().__init__(parent)
        self.data_dir, self.palettes = data_dir, load_local_index(data_dir)
        self.setWindowTitle("CPT-City Live — Colour Ramp Browser")
        self.resize(860, 640)
        layout = QVBoxLayout(self)
        intro = QLabel("Search, preview and install ramps from the live cpt-city QGIS catalogue.")
        layout.addWidget(intro)
        row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search palette, collection or path…")
        self.force = QCheckBox("Force full refresh")
        self.sync_button = QPushButton("Check for new palettes")
        row.addWidget(self.search, 1); row.addWidget(self.force); row.addWidget(self.sync_button)
        layout.addLayout(row)
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setIconSize(QSize(260, 28))
        layout.addWidget(self.list, 1)
        self.status, self.progress = QLabel(), QProgressBar()
        self.progress.setRange(0, 0); self.progress.hide()
        layout.addWidget(self.status); layout.addWidget(self.progress)
        buttons = QHBoxLayout()
        select_visible, install, close = QPushButton("Select visible"), QPushButton("Install selected in QGIS"), QPushButton("Close")
        buttons.addWidget(select_visible); buttons.addStretch(1); buttons.addWidget(install); buttons.addWidget(close)
        layout.addLayout(buttons)
        self.search.textChanged.connect(self.populate)
        self.sync_button.clicked.connect(self.sync)
        select_visible.clicked.connect(self.list.selectAll)
        install.clicked.connect(self.install_selected)
        close.clicked.connect(self.accept)
        self.populate()

    def populate(self):
        query = self.search.text().strip().lower()
        self.list.clear()
        for palette in self.palettes:
            if query and query not in palette.search_text: continue
            item = QListWidgetItem(preview_icon(palette), f"{palette.name}   —   {palette.collection}")
            item.setToolTip(palette.relative_path); item.setData(Qt.UserRole, palette)
            self.list.addItem(item)
        self.status.setText(f"Showing {self.list.count():,} of {len(self.palettes):,} palettes")

    def sync(self):
        self.progress.show(); self.sync_button.setEnabled(False)
        try:
            remote, self.palettes, changed = sync_catalogue(self.data_dir, self.force.isChecked(), self._progress)
            self.populate()
            action = "Downloaded and indexed" if changed else "Already current; found"
            self.status.setText(f"{action} {len(self.palettes):,} palettes (cpt-city {remote.version}).")
            QSettings().setValue("cptCityLive/lastVersion", remote.version)
        except Exception as error:
            QMessageBox.critical(self, "CPT-City Live", f"Could not update the catalogue:\n\n{error}")
        finally:
            self.progress.hide(); self.sync_button.setEnabled(True)

    def _progress(self, message):
        self.status.setText(message); QgsApplication.processEvents()

    def install_selected(self):
        selected = self.list.selectedItems()
        if not selected:
            QMessageBox.information(self, "CPT-City Live", "Select one or more palettes first."); return
        style, installed = QgsStyle.defaultStyle(), 0
        for item in selected:
            palette = item.data(Qt.UserRole)
            style_name = f"cpt-city/{palette.key}"
            if style.addColorRamp(style_name, ramp_from_palette(palette), True):
                installed += 1
                try: style.tagSymbol(QgsStyle.ColorrampEntity, style_name, ["cpt-city", palette.collection])
                except Exception: pass
        style.save()
        QMessageBox.information(self, "CPT-City Live", f"Installed {installed:,} ramp(s).\n\nFind them in Style Manager by searching for cpt-city/.")

class CptCityLivePlugin:
    def __init__(self, iface):
        self.iface, self.action, self.dialog = iface, None, None
        self.data_dir = Path(QgsApplication.qgisSettingsDirPath()) / "cpt-city-live"

    def initGui(self):
        self.action = QAction(QIcon(str(Path(__file__).with_name("icon.svg"))), "CPT-City Live", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToRasterMenu("CPT-City Live", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginRasterMenu("CPT-City Live", self.action)
            self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dialog = PaletteDialog(self.data_dir, self.iface.mainWindow())
        self.dialog.show(); self.dialog.raise_(); self.dialog.activateWindow()
