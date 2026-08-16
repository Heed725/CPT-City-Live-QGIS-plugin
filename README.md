# CPT-City New Catalog for QGIS

This plugin adds the complete collection as a separate archive named `cpt-city-new`. It does **not** add 7,000+ entries directly to Style Manager. Collections remain grouped and QGIS loads a ramp only when selected.

QGIS's native dialog supports one active CPT-City archive at a time. The plugin activates `cpt-city-new`; its Restore action or the supplied Python script returns QGIS to the original built-in archive.

## Install and use

1. Download `CPT-City-New-Catalog-2.2.0.zip` from Releases.
2. In QGIS open **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Choose the downloaded ZIP and enable the plugin.
4. The plugin activates `cpt-city-new` automatically. You can also use **Raster → CPT-City Catalog → Activate CPT-City New catalog**.
5. In raster or vector symbology, open the colour-ramp menu and choose **Create New Color Ramp**.
6. In **Color ramp type**, choose **Catalog: cpt-city** and click **OK**.
7. Browse the grouped collections, choose a palette and accept it.

The plugin performs no palette network download on the user's computer. Its release contains the native SVG archive. It sets QGIS's `CptCity/baseDir` and `CptCity/archiveName`, then reinitializes `QgsCptCityArchive`. Ramps remain in the catalog and are not imported individually.

## Restore QGIS's original catalog

Use **Raster → CPT-City Catalog → Restore QGIS default CPT-City**. Alternatively, open QGIS's Python Console editor and run `scripts/restore_default_cpt_city.py` from the repository. The script removes the custom `CptCity/baseDir` and `CptCity/archiveName` settings and reinitializes the built-in archive.

## Apply to a raster

Open **Layer Properties → Symbology → Singleband pseudocolor**, open the colour-ramp selector, choose **Create New Color Ramp → Catalog: cpt-city**, browse to a ramp, select **Classify**, then apply.

## Updating the bundled archive

The release workflow discovers the current cpt-city `svg` package, safely extracts it under `cpt_city_live/archives/cpt-city-new`, adds archive metadata, and packages it inside the installable plugin ZIP.

## Licensing

The plugin code is MIT licensed. Individual palettes remain subject to their cpt-city contributor licences and attribution. See the [cpt-city copyright information](https://phillips.shef.ac.uk/pub/cpt-city/notes/copyright.html).
