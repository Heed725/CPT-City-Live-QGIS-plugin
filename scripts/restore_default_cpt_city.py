"""Run in the QGIS Python Console to restore QGIS's built-in CPT-City archive."""
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsCptCityArchive, QgsSettings

settings = QgsSettings()
old_base_dir = settings.value("CptCity/baseDir", "")
old_archive_name = settings.value("CptCity/archiveName", "")

settings.remove("CptCity/baseDir")
settings.remove("CptCity/archiveName")
QgsCptCityArchive.clearArchives()
QgsCptCityArchive.initDefaultArchive()

archive = QgsCptCityArchive.defaultArchive()
if archive is not None and not archive.isEmpty():
    message = (
        "QGIS's built-in CPT-City archive has been restored.\n\n"
        f"Removed base directory setting: {old_base_dir or '(not set)'}\n"
        f"Removed archive setting: {old_archive_name or '(not set)'}\n\n"
        "Restart QGIS before opening the color-ramp catalog."
    )
    print(message)
    QMessageBox.information(None, "Restore Default CPT-City", message)
else:
    message = "The custom CPT-City settings were removed, but QGIS did not initialize its built-in archive. Restart QGIS and try again."
    print(message)
    QMessageBox.warning(None, "Restore Default CPT-City", message)
