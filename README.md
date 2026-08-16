# CPT-City Offline Palette Installer for QGIS

This plugin ships with thousands of cpt-city colour ramps already converted into one QGIS XML bundle. End users do not browse or download an online catalogue: install the release ZIP, click **Install CPT-City palettes**, and use the ramps directly from QGIS symbology.

## Install and use

1. Download `CPT-City-Offline-2.0.0.zip` from Releases.
2. In QGIS open **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Choose the downloaded ZIP and enable the plugin.
4. Open **Raster → CPT-City Offline → Install CPT-City palettes** or use the toolbar button.
5. Click **Install palettes** and wait for the progress bar.
6. In raster or vector symbology, open the colour-ramp list and search for `cpt-city/`.

The plugin performs no palette network download on the user's computer. The complete `palettes.xml` is included by the release workflow. Installation into the QGIS Style database is processed in small batches so the interface remains responsive.

## Apply to a raster

Open **Layer Properties → Symbology → Singleband pseudocolor**, open the colour-ramp selector, search for `cpt-city/`, choose a ramp, select **Classify**, then apply.

## Updating the bundled archive

The release workflow runs `scripts/build_palette_bundle.py`. It discovers the current cpt-city `qgs` package, combines every `.qgs` ramp into `cpt_city_live/palettes.xml`, records its version/count in `bundle.json`, and packages both inside the installable plugin ZIP.

## Licensing

The plugin code is MIT licensed. Individual palettes remain subject to their cpt-city contributor licences and attribution. See the [cpt-city copyright information](https://phillips.shef.ac.uk/pub/cpt-city/notes/copyright.html).
