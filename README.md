# CPT-City New QGIS Plugin

A safe, separate color-ramp catalog containing the complete CPT-City SVG collection. It does not replace, initialize, or modify QGIS's built-in CPT-City archive.

## Safe independent catalog

The QGIS 3.40.1 native CPT-City browser can crash in `QgsCptCityBrowserModel::findPath` when a second full raw archive is registered. This plugin avoids that native mechanism completely.

- Independent plugin window named **CPT-City New Catalog**
- In-memory name/path index for fast search
- Folder hierarchy; at most 250 results displayed while browsing
- Only the selected SVG is parsed and previewed
- Only the selected ramp is installed in QGIS Style Manager
- Checks upstream CPT-City for new SVG package versions without blocking the window
- Downloads a newer catalog only when the user chooses to update
- Multi-selects palettes with Ctrl/Shift, or selects every visible search result
- No `QgsCptCityArchive`, `QgsCptCityColorRampDialog`, `clearArchives()`, or CPT-City settings changes
- Default QGIS CPT-City remains available and unchanged

## Install

1. Keep the old `cpt_city_live` folder disabled or delete that disabled copy.
2. Download `CPT-City-New-QGIS-Plugin-1.0.0.zip` from [Releases](https://github.com/Heed725/CPT-City-New-QGIS-Plugin/releases/tag/v1.0.0).
3. In QGIS select **Plugins → Manage and Install Plugins → Install from ZIP**.
4. Choose the ZIP and enable **CPT-City New Independent Catalog**.
5. Open **Raster → CPT-City New → CPT-City New Catalog**, or click its toolbar icon.

No QGIS restart is required after enabling the plugin.

## Use a ramp

1. Browse a collection or search by ramp/folder name.
2. Select one palette, Ctrl/Shift-select several palettes, or click **Select visible**.
3. Click **Install selected palette(s) in QGIS**.
4. Open a layer's symbology and its ordinary color-ramp selector.
5. Select the installed ramp. Installed names begin with `CPT-City New —`.

The thousands of unselected ramps remain in the plugin catalog and outside Style Manager.

## Detect and download new palettes

The window checks the CPT-City package page in the background. When a newer package version is detected, **Check for catalog updates** changes to **Download catalog update**. Downloading happens through Qt's network manager, keeps the interface responsive, validates ZIP paths, extracts to a staging directory, and replaces the separate catalog only after successful validation. A failed update keeps the existing catalog intact.

## Installing after recovery

The plugin never reads or restores the unsafe earlier configuration. If you followed the recovery commands and `Select-String` returned no result, your profile is already clean.

## Automatic upstream updates

The release workflow discovers the current CPT-City SVG package, extracts it under `cpt_city_live/archives/cpt-city-new`, creates a compact path index, and packages the installable ZIP. New upstream SVG ramps are included whenever a new release is built.

## Licensing

Plugin code is MIT licensed. Individual palettes retain their contributor licenses and attribution. See the [CPT-City copyright information](https://phillips.shef.ac.uk/pub/cpt-city/notes/copyright.html).
