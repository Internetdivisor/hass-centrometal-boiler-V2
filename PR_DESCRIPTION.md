## Summary

This PR adds full **PelTec II Lambda (`peltec2`)** device support and fixes a critical bug that affects all device types. It also modernises a number of deprecated Home Assistant APIs, corrects several long-standing sensor naming and unit errors, and introduces automatic exposure of unknown parameters from future firmware versions.

---

## 1. Critical bug fix — sensors and switches freezing at startup values

**Root cause:** All `update_callback` methods across the codebase contained an `if not self.enabled: return` guard. This guard returns `False` when the entity registry has not yet finished initialising, which means it blocks the very first websocket push events. Because the websocket protocol only sends *changes*, once that first update is missed the entity value is permanently stuck at its initial (startup) value and never recovers.

**Affected files and classes:**
- `sensors/WebBoilerGenericSensor.py` — `update_callback`
- `switches/WebBoilerPowerSwitch.py` — `update_callback`
- `switches/WebBoilerCircuitSwitch.py` — `update_callback`
- `binary_sensor.py` — `update_callback` in `WebBoilerWebsocketStatus`

**Fix:** The `if not self.enabled: return` guard has been removed from all four locations. Callbacks now unconditionally call `async_write_ha_state()`, which is the correct HA pattern for push-based entities.

This also resolves **issue #21** — circuit switches always showing the OFF state regardless of the actual boiler state.

---

## 2. New device support — PelTec II Lambda (`peltec2`)

`sensor.py` now detects `device["type"] == "peltec2"` and creates the following additional entities:

- **`WebBoilerOperationStateSensor`** — translates the `B_STATE` parameter (raw firmware stage codes) into human-readable strings covering all documented operating states: `OFF`, `S0`–`S7`, `SP1`–`SP5`, `D0`–`D6`, `PF0`–`PF4`, and `C0`
- All PelTec II-specific parameters are mapped in `generic_sensors_peltec.py` with proper names, units, icons, and device classes (see section 5 below)

---

## 3. New sensor class — `WebBoilerBinaryOnOffSensor`

New file `sensors/WebBoilerBinaryOnOffSensor.py`. A specialised sensor subclass that renders pump, fan, and heater parameters as `"ON"` / `"OFF"` text, normalising all raw value variants (integer 0/1, strings `"0"`/`"1"`, `"ON"`/`"OFF"`, boolean). Exposes the raw numeric value as an attribute.

Parameters handled: `B_CMD`, `B_Ppwm`, `B_P1`, `B_gri`, `B_fan01`, `K1B_onOff`, `K1B_P`.

---

## 4. New sensor class — `WebBoilerOperationStateSensor`

New file `sensors/WebBoilerOperationStateSensor.py`. Decodes the `B_STATE` string code reported by PelTec II firmware into a full descriptive label (e.g. `"D3: Power D3"`, `"S3: Waiting for flame"`, `"C0: Grate cleaning"`). Exposes the raw stage code as an attribute for automation use. Includes all 30 documented state codes.

---

## 5. Sensor name and unit corrections

Several parameters had incorrect or missing metadata:

| Parameter | Before | After |
|---|---|---|
| `B_Tptv1` | `"Domestic Hot Water"` (same name as `B_Tkm1`) — one was silently dropped | `"DHW Flow Temperature"` |
| `B_Tkm1` | `"Domestic Hot Water"` — duplicate, caused deduplication loss | `"DHW Boiler Temperature"` |
| `B_ODRTMP` | No unit, no device class | `°C`, `SensorDeviceClass.TEMPERATURE` |
| `K1B_korN` | No unit, no device class | `°C`, `SensorDeviceClass.TEMPERATURE` |

---

## 6. Heating circuit duplicate parameter fix

`K1B_CircType`, `K1B_korType`, and `K1B_dayNight` were defined in both the `PELTEC_GENERIC_SENSORS` map and generated again inside `WebBoilerHeatingCircuitSensor`. The second creation was silently dropped by HA's entity registry. These are now only created once via the heating circuit builder.

---

## 7. `device_state_attributes` → `extra_state_attributes`

The deprecated `device_state_attributes` property has been replaced with `extra_state_attributes` across all sensor and switch classes:
- `WebBoilerGenericSensor`
- `WebBoilerFireGridSensor`
- `WebBoilerBinaryOnOffSensor`
- `WebBoilerOperationStateSensor`
- `WebBoilerWorkingTableSensor`
- `WebBoilerPowerSwitch`
- `WebBoilerCircuitSwitch`

---

## 8. `SensorStateClass` added for measurable sensors

The `state_class` property is now properly implemented in `WebBoilerGenericSensor` to allow HA to record long-term statistics:

| Condition | State class |
|---|---|
| `SensorDeviceClass.TEMPERATURE` | `MEASUREMENT` |
| Percentage params (`B_razP`, `B_Oxy1`, `B_signal`, `B_misP`) | `MEASUREMENT` |
| `B_fan` | `MEASUREMENT` |
| `UnitOfTime.MINUTES` + name starts with `CNT_` | `TOTAL_INCREASING` |
| `CNT_1`, `CNT_7` | `TOTAL_INCREASING` |

---

## 9. New and corrected parameters in `generic_sensors_peltec.py`

New entries added:
- `B_fanB` — Fan B Speed (rpm)
- `B_WifiVER` — Wifi Box Version
- `B_razina` — Tank Level (Empty / Reserve / Full)
- `B_SUP_TYPE` — Supply Type (None / Pellet Screw / Vacuum)
- `B_PTV/GRI` — DHW / Heater active state (Yes/No)
- `B_PTV/GRI_SEL` — DHW / Heater Select (ON/OFF)
- `B_dop` — Additional Heating
- `B_doz` — Fuel Dosing
- `B_specG` — Special Combustion
- `B_start` — Start Signal

---

## 10. Heating circuit sensors — `_misC` and `_misO` added

`WebBoilerHeatingCircuitSensor` now creates two additional sensors per circuit:
- `{prefix}_misC` — Valve Closing (ON/OFF)
- `{prefix}_misO` — Valve Opening (ON/OFF)

The heating circuit builder also introduces two specialised subclasses:
- `WebBoilerHeatingCircuitBinarySensor` — renders pump/valve params as ON/OFF
- `WebBoilerHeatingCircuitDayNightSensor` — renders `_dayNight` params as Day / Night / Program

---

## 11. `WebBoilerPowerSwitch` — full rewrite

The power switch logic has been rewritten for correctness and reliability:

- `is_on` now first reads `B_CMD` (the explicit command flag) and falls back to reading `B_STATE != "OFF"` if `B_CMD` is absent or unavailable — matching actual boiler semantics
- `async_turn_on` / `async_turn_off` now call `refresh()` and then `notify_all_updated()` after the command so the entire UI updates atomically
- `extra_state_attributes` now exposes both `B_CMD` and `B_STATE` raw values for diagnostics
- Helper function `_value_is_on()` centralises value normalisation (handles `0`/`1`, `"ON"`/`"OFF"`, booleans)
- Supports `peltec2` device type (added to `switch.py` type check alongside `peltec`, `cmpelet`, `biopl`)

---

## 12. `WebBoilerCircuitSwitch` — rewrite

- `is_on` now compares `PVAL_{dbindex}_0` against `PMAX_{dbindex}_0` (the "on" value defined by the boiler) instead of checking for a raw `1`
- `extra_state_attributes` exposes `Last updated` timestamp
- All four parameters (`PDEF`, `PVAL`, `PMIN`, `PMAX`) register update callbacks so the switch state reflects live websocket pushes
- `__del__` and `async_added_to_hass` now fully symmetrical for callback setup and teardown

---

## 13. `sensor.py` — entity deduplication

`sensor.py` now runs a deduplication pass after collecting all entities. If two sensor factories produce an entity with the same `unique_id` (which could happen for parameters that appear in multiple device type maps), the second is dropped and a debug log entry is emitted. This replaces the previous silent drop by the HA entity registry.

---

## 14. `__init__.py` — `WebBoilerSystem` rewrite

The core integration class has been substantially refactored:

- `start_tick()` / `cancel_tick()` methods extracted for clean lifecycle management
- `tick()` now has guarded exception handling — a crashed tick no longer kills the polling loop
- `relogin()` extracted as a separate method; closes both websocket and HTTP session before attempting re-authentication
- `async_unload_entry` now cancels the tick and closes the websocket with individual try/except blocks to guarantee clean teardown even if one step fails

---

## 15. Automatic exposure of unknown parameters

`WebBoilerGenericSensor.create_unknown_entities()` now auto-creates a sensor for any parameter returned by the boiler that is not claimed by any of the existing sensor factories. These sensors are **hidden by default** (`entity_registry_enabled_default = False`) and use the `mdi:help-circle-outline` icon, so they do not clutter the UI but are available for diagnostics or future firmware parameters.

Internally known noise parameters (`PING`, `B_Time`, `CMD`, `CMD_TIME`, `SE00`–`SE02`, `wf_req`, and several duplicate demand-state parameters) are excluded from this list.

---

## 16. `manifest.json` changes

| Field | Old value | New value |
|---|---|---|
| `version` | `0.0.54` | `0.0.55` |
| `requirements` | `py-centrometal-web-boiler==0.0.58` | `py-centrometal-web-boiler==0.0.59` |

The `libs/` directory containing a bundled wheel has been removed. The library is now distributed via PyPI as `0.0.59` and installed automatically by Home Assistant.

---

## 17. Library — `py-centrometal-web-boiler` 0.0.59

Changes relative to the last published version (0.0.58):
- SSL connection fixes for the `wss://web-boiler.com:15671/ws` endpoint
- Significantly reduced log verbosity (removed noisy debug-level lines from the websocket keep-alive and STOMP frame parsing paths)

This should be published to PyPI as `py-centrometal-web-boiler==0.0.59` (PR submitted separately to the [py-centrometal-web-boiler](https://github.com/9a4gl/py-centrometal-web-boiler) repository).

---

## Testing

165 unit tests pass covering the full callback chain from websocket frame arrival through parameter update to sensor state write.
