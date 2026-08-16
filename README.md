# CPT-City New Catalog for QGIS

This plugin adds the complete collection as a separate archive named `cpt-city-new`. It does **not** add 7,000+ entries directly to Style Manager. Collections remain grouped and QGIS loads a ramp only when selected.

QGIS's native dialog supports one active CPT-City archive at a time. The plugin safely configures `cpt-city-new` and requires QGIS to be restarted before it becomes active.

## Install and use

1. Download `CPT-City-New-Catalog-2.2.2.zip` from Releases.
2. In QGIS open **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Choose the downloaded ZIP and enable the plugin.
4. The plugin saves the `cpt-city-new` configuration. Restart QGIS once.
5. You can also use **Raster → CPT-City Catalog → Activate CPT-City New catalog**, then restart QGIS.
5. In raster or vector symbology, open the colour-ramp menu and choose **Create New Color Ramp**.
6. In **Color ramp type**, choose **Catalog: cpt-city** and click **OK**.
7. Browse the grouped collections, choose a palette and accept it.

The plugin performs no palette network download on the user's computer. Its release contains the native SVG archive. It sets QGIS's `CptCity/baseDir` and `CptCity/archiveName`, then reinitializes `QgsCptCityArchive`. Ramps remain in the catalog and are not imported individually.

The plugin deliberately does not call `QgsCptCityArchive.clearArchives()` or replace an existing archive during a live QGIS session. When no archive is initialized, it safely calls `initArchive()` for `cpt-city-new`; otherwise it asks for a restart.

## Apply to a raster

Open **Layer Properties → Symbology → Singleband pseudocolor**, open the colour-ramp selector, choose **Create New Color Ramp → Catalog: cpt-city**, browse to a ramp, select **Classify**, then apply.

## Updating the bundled archive

The release workflow discovers the current cpt-city `svg` package, safely extracts it under `cpt_city_live/archives/cpt-city-new`, adds archive metadata, and packages it inside the installable plugin ZIP.

## Licensing

The plugin code is MIT licensed. Individual palettes remain subject to their cpt-city contributor licences and attribution. See the [cpt-city copyright information](https://phillips.shef.ac.uk/pub/cpt-city/notes/copyright.html).
