# Changelog

## [0.0.60] - 2026-03-14

### Fixed
- **Critical**: Removed `if not self.enabled` guard from all `update_callback` methods. This guard silently blocked every websocket push update, causing all sensors and switches to freeze at startup values and never update again. Fixes issue #21 (circuit switches always showing OFF).
- `B_Tptv1` and `B_Tkm1` both generated `sensor.*_dhw_temperature` — only one survived. Now "DHW Flow Temperature" and "DHW Boiler Temperature".
- `K1B_CircType`, `K1B_korType`, `K1B_dayNight` duplicated between sensor maps — now created once.
- `B_ODRTMP` now has `°C` unit and `SensorDeviceClass.TEMPERATURE`.
- `K1B_korN` (Night Correction) now has `°C` unit and `SensorDeviceClass.TEMPERATURE`.
- `device_state_attributes` (deprecated) replaced with `extra_state_attributes` everywhere.

### Added
- Full `peltec2` (PelTec II Lambda) device type support.
- `WebBoilerOperationStateSensor`: translates `B_STATE` codes to human-readable strings (OFF, S0-S7, SP1-SP5, D0-D6, PF0-PF4, C0).
- `WebBoilerBinaryOnOffSensor`: ON/OFF display for `B_CMD`, `B_Ppwm`, `B_P1`, `B_gri`, `B_fan01`, `K1B_onOff`, `K1B_P`.
- Yes/No display for: `B_fireS`, `B_doz`, `B_start`, `B_specG`, `B_dop`, `B_zahPa`, `B_Valve`, `B_P2-4`, `B_Paku`, `B_Pk1_k2`, `B_VAC_STS`, `B_VAC_TUR`, `B_cm2k`, `B_PTV/GRI`, `B_PTV/GRI_SEL`.
- `B_razina` shows Empty / Reserve / Full.
- `B_SUP_TYPE` shows None / Pellet Screw / Vacuum.
- `B_fanB` (Fan B Speed), `B_WifiVER` (WiFi Box Version) sensors.
- `_misC` / `_misO` (Valve Closing/Opening) per heating circuit.
- `_korN`, `_Prec`, `_zahP` per heating circuit.
- All PelTec II specific parameters mapped with proper names and icons.
- `SensorStateClass.MEASUREMENT` for temperature/percentage sensors.
- `SensorStateClass.TOTAL_INCREASING` for counters (CNT_*).
- Unknown parameters auto-exposed as sensors, hidden in entity registry by default.
- Bundled `py-centrometal-web-boiler==0.0.60` with SSL fixes.
- Entity deduplication at setup time.

### Removed
- `WebBoilerCurrentTimeSensor` (unused).
- `WebBoilerBinaryStateSensor` (replaced by `WebBoilerBinaryOnOffSensor`).
- `WebBoilerPelletLevelSensor` (logic merged into `WebBoilerGenericSensor`).
- Runtime monkey patches from `__init__.py` (baked into bundled wheel).
- Duplicate raw 0/1 params: `B_zahPpwm`, `B_zahP1`, `B_zahK1_K2`, `B_zahValve`, `B_PTV_PRI`.
