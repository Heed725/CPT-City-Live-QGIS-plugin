# CPT-City New Independent Catalog for QGIS

A safe, separate color-ramp catalog containing the complete CPT-City SVG collection. It does not replace, initialize, or modify QGIS's built-in CPT-City archive.

## Why version 3 is different

The QGIS 3.40.1 native CPT-City browser can crash in `QgsCptCityBrowserModel::findPath` when a second full raw archive is registered. Earlier 2.x releases used that native mechanism. Version 3 removes it completely.

- Independent plugin window named **CPT-City New Catalog**
- In-memory name/path index for fast search
- Folder hierarchy; at most 250 results displayed while browsing
- Only the selected SVG is parsed and previewed
- Only the selected ramp is installed in QGIS Style Manager
- No `QgsCptCityArchive`, `QgsCptCityColorRampDialog`, `clearArchives()`, or CPT-City settings changes
- Default QGIS CPT-City remains available and unchanged

## Install

1. Keep the old `cpt_city_live` folder disabled or delete that disabled copy.
2. Download `CPT-City-New-Independent-Catalog-3.0.0.zip` from Releases.
3. In QGIS select **Plugins → Manage and Install Plugins → Install from ZIP**.
4. Choose the ZIP and enable **CPT-City New Independent Catalog**.
5. Open **Raster → CPT-City New → CPT-City New Catalog**, or click its toolbar icon.

No QGIS restart is required after enabling version 3.

## Use a ramp

1. Browse a collection or search by ramp/folder name.
2. Click a ramp to generate its preview.
3. Click **Install selected ramp in QGIS**.
4. Open a layer's symbology and its ordinary color-ramp selector.
5. Select the installed ramp. Installed names begin with `CPT-City New —`.

The thousands of unselected ramps remain in the plugin catalog and outside Style Manager.

## Upgrading from 2.x after recovery

Version 3 never reads or restores the unsafe 2.x configuration. If you followed the recovery commands and `Select-String` returned no result, your profile is already clean.

## Automatic upstream updates

The release workflow discovers the current CPT-City SVG package, extracts it under `cpt_city_live/archives/cpt-city-new`, creates a compact path index, and packages the installable ZIP. New upstream SVG ramps are included whenever a new release is built.

## Licensing

Plugin code is MIT licensed. Individual palettes retain their contributor licenses and attribution. See the [CPT-City copyright information](https://phillips.shef.ac.uk/pub/cpt-city/notes/copyright.html).

