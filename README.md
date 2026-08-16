# CPT-City Native Catalog for QGIS

This plugin adds the complete cpt-city collection to QGIS's native hierarchical colour-ramp catalog. It does **not** add 7,000+ entries directly to Style Manager. Collections remain grouped by author/folder and QGIS loads a ramp only when the user selects it.

## Install and use

1. Download `CPT-City-Native-Catalog-2.1.0.zip` from Releases.
2. In QGIS open **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Choose the downloaded ZIP and enable the plugin.
4. The plugin activates the bundled catalog automatically. You can also use **Raster → CPT-City Catalog → Activate CPT-City colour catalog**.
5. In raster or vector symbology, open the colour-ramp menu and choose **Create New Color Ramp**.
6. In **Color ramp type**, choose **Catalog: cpt-city** and click **OK**.
7. Browse the grouped collections, choose a palette and accept it.

The plugin performs no palette network download on the user's computer. Its release contains the native SVG archive. It sets QGIS's `CptCity/baseDir` and `CptCity/archiveName`, then reinitializes `QgsCptCityArchive`. Ramps remain in the catalog and are not imported individually.

## Apply to a raster

Open **Layer Properties → Symbology → Singleband pseudocolor**, open the colour-ramp selector, choose **Create New Color Ramp → Catalog: cpt-city**, browse to a ramp, select **Classify**, then apply.

## Updating the bundled archive

The release workflow discovers the current cpt-city `svg` package, safely extracts it under `cpt_city_live/archives/cpt-city-full`, adds archive metadata, and packages it inside the installable plugin ZIP.

## Licensing

The plugin code is MIT licensed. Individual palettes remain subject to their cpt-city contributor licences and attribution. See the [cpt-city copyright information](https://phillips.shef.ac.uk/pub/cpt-city/notes/copyright.html).
