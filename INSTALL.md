# Centrometal Boiler — Installation Guide

## HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/9a4gl/hass-centrometal-boiler` as an **Integration**
3. Search for **Centrometal Boiler System** and install
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → search **Centrometal**

## Manual installation

1. Download the latest release from the [Releases page](https://github.com/9a4gl/hass-centrometal-boiler/releases)
2. Copy the `centrometal_boiler/` folder into `/config/custom_components/`
3. Restart Home Assistant
4. Settings → Devices & Services → Add Integration → search **Centrometal**

The required library (`py-centrometal-web-boiler`) is installed automatically by Home Assistant from PyPI.

## Updating from a previous version

1. Settings → Devices & Services → Centrometal Boiler → Delete
2. Restart Home Assistant
3. Delete `/config/custom_components/centrometal_boiler/` (via File Editor or Samba)
4. Follow the installation steps above
