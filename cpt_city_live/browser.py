"""Independent lazy browser; it never registers a QgsCptCityArchive."""
from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from qgis.PyQt.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QSplitter,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from qgis.core import QgsGradientColorRamp, QgsGradientStop, QgsStyle

from .core import display_name, load_index, parse_svg


class CatalogDialog(QDialog):
    def __init__(self, iface, plugin_dir):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.plugin_dir = Path(plugin_dir)
        self.archive = self.plugin_dir / "archives" / "cpt-city-new"
        self.paths = load_index(self.plugin_dir)
        self.current_stops = None
        self.current_path = None
        self.setWindowTitle("CPT-City New — Independent Colour Ramp Catalog")
        self.resize(980, 680)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self._build_ui()
        self._build_tree()
        self._show_paths(self.paths[:250], limited=len(self.paths) > 250)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        intro = QLabel("Browse the separate CPT-City New catalog. Only the selected SVG is loaded; the default QGIS CPT-City archive is never changed.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search 7,000+ ramps by name or folder…")
        self.search.textChanged.connect(self._search)
        layout.addWidget(self.search)
        splitter = QSplitter()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Collections")
        self.tree.itemSelectionChanged.connect(self._folder_selected)
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.currentItemChanged.connect(self._ramp_selected)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.list)
        splitter.setSizes([300, 650])
        layout.addWidget(splitter, 1)
        self.preview = QLabel("Select a ramp to preview it")
        self.preview.setMinimumHeight(76)
        self.preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview)
        self.status = QLabel()
        layout.addWidget(self.status)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.install = QPushButton("Install selected ramp in QGIS")
        self.install.setEnabled(False)
        self.install.clicked.connect(self._install)
        buttons.addWidget(self.install)
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        buttons.addWidget(close)
        layout.addLayout(buttons)

    def _build_tree(self):
        root_item = QTreeWidgetItem([f"All ramps ({len(self.paths)})"])
        root_item.setData(0, Qt.UserRole, "")
        self.tree.addTopLevelItem(root_item)
        nodes = {"": root_item}
        counts = {}
        for relative in self.paths:
            current = ""
            for part in relative.split("/")[:-1]:
                parent = current
                current = f"{current}/{part}".strip("/")
                counts[current] = counts.get(current, 0) + 1
                if current not in nodes:
                    item = QTreeWidgetItem([part])
                    item.setData(0, Qt.UserRole, current)
                    nodes[parent].addChild(item)
                    nodes[current] = item
        for path, item in nodes.items():
            if path:
                item.setText(0, f"{Path(path).name} ({counts[path]})")
        root_item.setExpanded(True)
        self.tree.setCurrentItem(root_item)

    def _show_paths(self, paths, limited=False):
        self.list.clear()
        for relative in paths:
            item = QListWidgetItem(display_name(relative))
            item.setToolTip(relative)
            item.setData(Qt.UserRole, relative)
            self.list.addItem(item)
        suffix = " (first results shown; search or choose a folder)" if limited else ""
        self.status.setText(f"{len(paths)} visible ramp(s){suffix}")

    def _folder_selected(self):
        item = self.tree.currentItem()
        if not item:
            return
        prefix = item.data(0, Qt.UserRole)
        matches = [p for p in self.paths if not prefix or p.startswith(prefix + "/")]
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self._show_paths(matches[:250], limited=len(matches) > 250)

    def _search(self, text):
        query = text.strip().lower()
        if not query:
            self._folder_selected()
            return
        matches = [p for p in self.paths if query in p.lower()]
        self._show_paths(matches[:500], limited=len(matches) > 500)

    def _ramp_selected(self, current, previous):
        self.install.setEnabled(False)
        self.current_stops = None
        if current is None:
            return
        relative = current.data(Qt.UserRole)
        try:
            stops = parse_svg(self.archive / relative)
        except Exception as error:
            self.preview.setText(f"Could not read {relative}: {error}")
            return
        self.current_path, self.current_stops = relative, stops
        pixmap = QPixmap(820, 58)
        gradient = QLinearGradient(0, 0, pixmap.width(), 0)
        for offset, rgb in stops:
            gradient.setColorAt(offset, QColor(*rgb))
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), gradient)
        painter.end()
        self.preview.setPixmap(pixmap)
        self.preview.setToolTip(relative)
        self.install.setEnabled(True)
        self.status.setText(f"Selected: {relative} — {len(stops)} stops")

    def _install(self):
        if not self.current_stops:
            return
        colors = [(offset, QColor(*rgb)) for offset, rgb in self.current_stops]
        interior = [QgsGradientStop(offset, color) for offset, color in colors[1:-1]]
        ramp = QgsGradientColorRamp(colors[0][1], colors[-1][1], False, interior)
        base_name = "CPT-City New — " + self.current_path[:-4].replace("/", " — ")
        style = QgsStyle.defaultStyle()
        name, number = base_name, 2
        while name in style.colorRampNames():
            name = f"{base_name} ({number})"
            number += 1
        if style.addColorRamp(name, ramp, True):
            QMessageBox.information(self, "Ramp installed", f"‘{name}’ was added to QGIS Style Manager.\n\nIt is now available in colour-ramp selectors as a standard gradient.")
        else:
            QMessageBox.warning(self, "Installation failed", "QGIS could not add the selected ramp to Style Manager.")

