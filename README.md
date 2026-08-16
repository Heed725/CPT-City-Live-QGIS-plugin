# CPT-City Live — QGIS Plugin

CPT-City Live discovers, previews and installs colour ramps from the live [cpt-city archive](https://phillips.shef.ac.uk/pub/cpt-city/).

It does **not** hard-code the current download ID. On every update check it reads the cpt-city package page, finds the link labelled **qgs**, detects the published version/resource, downloads the current ZIP and rebuilds its searchable index. When cpt-city publishes a new package containing new palettes, the plugin detects them.

## Features

- Live discovery of the current cpt-city QGIS package
- Search by palette name, collection/author or archive path
- Real ramp previews inside QGIS
- Multiple selection and filtered bulk installation
- Imports ramps into the active QGIS Style database
- Uses `cpt-city/collection/name` to avoid name collisions
- Records version, SHA-256, ETag and Last-Modified metadata
- Safe ZIP extraction and offline use of the last successful index
- QGIS 3.22–3.x support

## Install

1. Download `CPT-City-Live-1.0.0.zip`.
2. In QGIS open **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Select the ZIP and install it.
4. Open **Raster → CPT-City Live** or click the toolbar icon.
5. Click **Check for new palettes** the first time.
6. Search/select ramps and click **Install selected in QGIS**.

Installed ramps appear under **Settings → Style Manager → Color Ramps** and in symbology ramp selectors. Search for `cpt-city/`.

## How new-palette detection works

The plugin requests `https://phillips.shef.ac.uk/pub/cpt-city/pkg` and parses the anchor whose visible label is `qgs`. A changed package resource triggers download and complete re-indexing, so the numeric resource URL may change without breaking the plugin.

Detection occurs after archive maintainers publish a palette in the downloadable QGIS package. Enable **Force full refresh** if the ZIP contents are replaced without changing its link.

## Development install

Copy `cpt_city_live` into the QGIS profile plugin directory, restart QGIS, then enable the plugin:

- Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins`
- Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
- macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`

## Privacy, attribution and licensing

The plugin contacts only `phillips.shef.ac.uk` when the update button is clicked and sends no credentials or project data. The plugin source is MIT licensed. Palettes are separate works by cpt-city contributors and retain their own licensing/copyright metadata in `COPYING.yaml` files and QGIS style comments. The plugin ZIP does not bundle the palette archive.
