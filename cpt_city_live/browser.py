"""Independent lazy browser; it never registers a QgsCptCityArchive."""
from pathlib import Path

from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qgis.PyQt.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QSplitter,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from qgis.core import QgsApplication, QgsGradientColorRamp, QgsGradientStop, QgsStyle

from .core import display_name, load_index, parse_svg
from .updater import PACKAGE_PAGE, discover_svg_package, install_zip, installed_version
from .user_catalog import catalog_directory, load_catalog, save_ramps


class CatalogDialog(QDialog):
    def __init__(self, iface, plugin_dir):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.plugin_dir = Path(plugin_dir)
        self.archive = self.plugin_dir / "archives" / "cpt-city-new"
        self.paths = load_index(self.plugin_dir)
        self.profile_dir = Path(QgsApplication.qgisSettingsDirPath())
        self.my_records = load_catalog(self.profile_dir)
        self.current_stops = None
        self.current_path = None
        self.network = QNetworkAccessManager(self)
        self.remote_url = None
        self.remote_version = None
        self.setWindowTitle("CPT-City New — Independent Colour Ramp Catalog")
        self.resize(980, 680)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self._build_ui()
        self._build_tree()
        self._show_paths(self.paths[:250], limited=len(self.paths) > 250)
        self._check_updates(silent=True)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        intro = QLabel("Browse the separate CPT-City New catalog. Only the selected SVG is loaded; the default QGIS CPT-City archive is never changed.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search 7,000+ ramps by name or folder…")
        self.search.textChanged.connect(self._search)
        layout.addWidget(self.search)
        update_row = QHBoxLayout()
        self.update_label = QLabel(f"Bundled CPT-City version: {installed_version(self.plugin_dir)}")
        update_row.addWidget(self.update_label)
        update_row.addStretch(1)
        self.update_button = QPushButton("Check for catalog updates")
        self.update_button.clicked.connect(lambda: self._check_updates(silent=False))
        update_row.addWidget(self.update_button)
        layout.addLayout(update_row)
        splitter = QSplitter()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Collections")
        self.tree.itemSelectionChanged.connect(self._folder_selected)
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
        self.select_visible = QPushButton("Select visible")
        self.select_visible.clicked.connect(self.list.selectAll)
        buttons.addWidget(self.select_visible)
        buttons.addStretch(1)
        self.save_catalog = QPushButton("Save selected to My Catalog")
        self.save_catalog.clicked.connect(self._save_selected)
        buttons.addWidget(self.save_catalog)
        self.install = QPushButton("Copy selected to QGIS Style Manager")
        self.install.setEnabled(False)
        self.install.clicked.connect(self._install)
        buttons.addWidget(self.install)
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        buttons.addWidget(close)
        layout.addLayout(buttons)

    def _save_selected(self):
        selected = self.list.selectedItems()
        if not selected:
            QMessageBox.information(self, "My Catalog", "Select one or more palettes first.")
            return
        sources = []
        for item in selected:
            identifier = item.data(Qt.UserRole)
            sources.append((self._source_name(identifier), self._svg_path(identifier)))
        try:
            added, total = save_ramps(self.profile_dir, sources)
            self.my_records = load_catalog(self.profile_dir)
            self.tree.clear()
            self._build_tree()
            QMessageBox.information(
                self, "Saved to My Catalog",
                f"Saved {added} new palette(s). My Catalog now contains {total} palette(s).\n\n"
                "Nothing was added to QGIS Style Manager."
            )
        except Exception as error:
            QMessageBox.critical(self, "Could not save palettes", str(error))

    def _build_tree(self):
        root_item = QTreeWidgetItem([f"All ramps ({len(self.paths)})"])
        root_item.setData(0, Qt.UserRole, "")
        self.tree.addTopLevelItem(root_item)
        my_item = QTreeWidgetItem([f"My Catalog ({len(self.my_records)})"])
        my_item.setData(0, Qt.UserRole, "__my_catalog__")
        self.tree.addTopLevelItem(my_item)
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
        if prefix == "__my_catalog__":
            self.list.clear()
            for record in self.my_records:
                item = QListWidgetItem(record["name"])
                item.setToolTip("My Catalog — " + record["source"])
                item.setData(Qt.UserRole, "MY:" + record["file"])
                self.list.addItem(item)
            self.status.setText(f"{len(self.my_records)} palette(s) saved in My Catalog")
            return
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
        svg_path = self._svg_path(relative)
        try:
            stops = parse_svg(svg_path)
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

    def _svg_path(self, identifier):
        if identifier.startswith("MY:"):
            return catalog_directory(self.profile_dir) / identifier[3:]
        return self.archive / identifier

    def _source_name(self, identifier):
        if not identifier.startswith("MY:"):
            return identifier
        relative = identifier[3:]
        for record in self.my_records:
            if record["file"] == relative:
                return record["source"]
        return Path(relative).name

    def _install(self):
        selected = self.list.selectedItems()
        if not selected:
            return
        style = QgsStyle.defaultStyle()
        installed, failed = [], []
        for item in selected:
            relative = item.data(Qt.UserRole)
            try:
                stops = parse_svg(self._svg_path(relative))
                colors = [(offset, QColor(*rgb)) for offset, rgb in stops]
                interior = [QgsGradientStop(offset, color) for offset, color in colors[1:-1]]
                ramp = QgsGradientColorRamp(colors[0][1], colors[-1][1], False, interior)
                source_name = self._source_name(relative)
                base_name = "CPT-City New — " + source_name[:-4].replace("/", " — ")
                name, number = base_name, 2
                while name in style.colorRampNames():
                    name = f"{base_name} ({number})"
                    number += 1
                if style.addColorRamp(name, ramp, True):
                    installed.append(name)
                else:
                    failed.append(relative)
            except Exception:
                failed.append(relative)
        message = f"Installed {len(installed)} palette(s) in QGIS Style Manager."
        if failed:
            message += f"\n\n{len(failed)} palette(s) could not be installed."
        QMessageBox.information(self, "Palette installation complete", message)

    def _check_updates(self, silent=False):
        self.update_button.setEnabled(False)
        self.update_button.setText("Checking…")
        reply = self.network.get(QNetworkRequest(QUrl(PACKAGE_PAGE)))
        reply.finished.connect(lambda: self._update_page_received(reply, silent))

    def _update_page_received(self, reply, silent):
        self.update_button.setEnabled(True)
        self.update_button.setText("Check for catalog updates")
        if reply.error():
            if not silent:
                QMessageBox.warning(self, "Update check failed", reply.errorString())
            reply.deleteLater()
            return
        try:
            self.remote_url, self.remote_version = discover_svg_package(bytes(reply.readAll()).decode("utf-8", "replace"))
            local = installed_version(self.plugin_dir)
            if self.remote_version == local:
                self.update_label.setText(f"Catalog is current: CPT-City {local}")
                if not silent:
                    QMessageBox.information(self, "Catalog is current", f"You already have CPT-City {local}.")
            else:
                self.update_label.setText(f"Update available: {local} → {self.remote_version}")
                self.update_button.setText("Download catalog update")
                try:
                    self.update_button.clicked.disconnect()
                except TypeError:
                    pass
                self.update_button.clicked.connect(self._download_update)
        except Exception as error:
            if not silent:
                QMessageBox.warning(self, "Update check failed", str(error))
        reply.deleteLater()

    def _download_update(self):
        if not self.remote_url:
            return
        self.update_button.setEnabled(False)
        self.update_button.setText("Downloading…")
        reply = self.network.get(QNetworkRequest(QUrl(self.remote_url)))
        reply.downloadProgress.connect(lambda received, total: self.update_label.setText(f"Downloading update: {received // 1048576} / {max(total, 0) // 1048576} MB"))
        reply.finished.connect(lambda: self._update_downloaded(reply))

    def _update_downloaded(self, reply):
        self.update_button.setEnabled(True)
        self.update_button.setText("Check for catalog updates")
        if reply.error():
            QMessageBox.warning(self, "Update failed", reply.errorString())
            reply.deleteLater()
            return
        try:
            count = install_zip(bytes(reply.readAll()), self.plugin_dir, self.remote_version)
            self.paths = load_index(self.plugin_dir)
            self.tree.clear()
            self._build_tree()
            self._show_paths(self.paths[:250], limited=len(self.paths) > 250)
            self.update_label.setText(f"Catalog updated: CPT-City {self.remote_version} ({count} ramps)")
            try:
                self.update_button.clicked.disconnect()
            except TypeError:
                pass
            self.update_button.clicked.connect(lambda: self._check_updates(silent=False))
            QMessageBox.information(self, "Catalog updated", f"CPT-City {self.remote_version} is ready with {count} ramps.")
        except Exception as error:
            QMessageBox.critical(self, "Update failed", f"The existing catalog was kept unchanged.\n\n{error}")
        reply.deleteLater()
