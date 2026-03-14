[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Maintenance](https://img.shields.io/maintenance/yes/2026.svg)

# hass-centrometal-boiler

Home Assistant custom component integration for Centrometal Boiler System (with CM WiFi-Box).

To visualize boiler display as card use https://github.com/9a4gl/lovelace-centrometal-boiler-card card.

## About

This is a fork of the original [hass-centrometal-boiler](https://github.com/9a4gl/hass-centrometal-boiler) by Tihomir Heidelberg, maintained by [Internetdivisor](https://github.com/Internetdivisor) with full PelTec II Lambda support and critical bug fixes.

This component connects to the Centrometal web boiler system to provide real-time sensor data and control in Home Assistant. No official API documentation exists — this is based on analysis of Centrometal's web application.

## Supported devices

- **PelTec II Lambda** (`peltec2`) ← added in this fork
- PelTec-lambda, PelTec (`peltec`)
- CentroPlus + Cm Pelet-set (`cmpelet`)
- BioTec-L (`biotec`)
- BioTec-Plus / Morvan GMX EASY (`biopl`)
- EKO-CK P + Cm Pelet-set
- Compact variants

## What's fixed in this fork

- **Critical**: Websocket push updates now correctly reach all sensors and switches. The original code had an `if not self.enabled` guard in all callback methods that silently blocked every real-time update — sensors and switches froze at startup values and never updated. This fixes issue #21 (circuit switches always showing OFF state).
- Full **PelTec II Lambda** (`peltec2`) device type support with correct operation state translation (OFF / S0-S7 / D0-D6 / PF / C0).
- `B_Tptv1` and `B_Tkm1` are now correctly named "DHW Flow Temperature" and "DHW Boiler Temperature" — previously both were called "DHW Temperature" causing one to be silently dropped.
- Binary sensors (`B_Ppwm`, `B_P1`, `B_gri`, `B_fan01`, `K1B_onOff`, `K1B_P`) now show ON/OFF instead of raw 0/1.
- Boolean sensors (`B_fireS`, `B_doz`, `B_start`, and others) show Yes/No instead of 0/1.
- Tank level (`B_razina`) shows Empty / Reserve / Full.
- Supply type (`B_SUP_TYPE`) shows None / Pellet Screw / Vacuum.
- Added `B_fanB`, `B_WifiVER`, heating circuit Valve Closing/Opening sensors.
- Temperature units and device classes fixed for `B_ODRTMP` and `K1B_korN`.
- Duplicate sensor entries removed between generic and heating circuit maps.
- Unknown parameters from future firmware versions are auto-exposed, hidden by default.
- Bundled `py-centrometal-web-boiler==0.0.60` with SSL fixes — no external PyPI dependency.
- Removed all deprecated HA APIs (`device_state_attributes` → `extra_state_attributes`).
- Correct `SensorStateClass` for history graphs and energy dashboard.

See [CHANGELOG.md](CHANGELOG.md) for the full list of changes.

## Installation

Requires Home Assistant 2024.11.2 or newer.

### Manual installation

```bash
cd /config
git clone https://github.com/Internetdivisor/hass-centrometal-boiler-V2.git
mkdir -p custom_components
cd custom_components
ln -s ../hass-centrometal-boiler-V2/custom_components/centrometal_boiler
```

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/Internetdivisor/hass-centrometal-boiler-V2` as type **Integration**
3. Install "Centrometal Boiler System" and restart Home Assistant

## Configuration

Settings → Integrations → Add Integration → search "Centrometal Boiler System" → enter your web-boiler.com e-mail and password.

## Services

`centrometal_boiler.turn` — Start or stop the boiler.

## Debugging

```yaml
logger:
  default: info
  logs:
    custom_components.centrometal_boiler: debug
    centrometal_web_boiler: debug
```
