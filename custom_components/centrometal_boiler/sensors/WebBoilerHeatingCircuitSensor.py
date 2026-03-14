import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from .WebBoilerGenericSensor import WebBoilerGenericSensor

_LOGGER = logging.getLogger(__name__)


class WebBoilerHeatingCircuitSensor:
    @staticmethod
    def create_heating_circuits_entities(hass: HomeAssistant, device) -> list[SensorEntity]:
        entities: list[SensorEntity] = []
        for i in range(1, 5):
            prefix = f"C{i}B"
            if WebBoilerHeatingCircuitSensor.device_has_prefix(device, prefix):
                entities.extend(
                    WebBoilerHeatingCircuitSensor.create_heating_circuit_entities(
                        hass, device, prefix, f"Circuit {i}"
                    )
                )
        for i in range(1, 5):
            prefix = f"K{i}B"
            if WebBoilerHeatingCircuitSensor.device_has_prefix(device, prefix):
                entities.extend(
                    WebBoilerHeatingCircuitSensor.create_heating_circuit_entities(
                        hass, device, prefix, f"Circuit {i}K"
                    )
                )
        return entities

    @staticmethod
    def device_has_prefix(device, prefix):
        for param in device["parameters"].keys():
            if param.startswith(prefix):
                return True
        return False

    @staticmethod
    def create_heating_circuit_entities(hass, device, prefix, name) -> list[SensorEntity]:
        entities: list[SensorEntity] = []
        items: dict[str, list] = {
            prefix + "_CircType": [None, "mdi:view-list", None, name + " Heating Type"],
            prefix + "_dayNight": [None, "mdi:view-list", None, name + " Day Night Mode"],
            prefix + "_kor":      [UnitOfTemperature.CELSIUS, "mdi:thermometer", SensorDeviceClass.TEMPERATURE, name + " Room Target Correction"],
            prefix + "_korN":     [UnitOfTemperature.CELSIUS, "mdi:thermometer-plus", SensorDeviceClass.TEMPERATURE, name + " Night Correction"],
            prefix + "_korType":  [None, "mdi:view-list", None, name + " Correction Type"],
            prefix + "_onOff":    [None, "mdi:pump", None, name + " Pump Demand"],
            prefix + "_P":        [None, "mdi:pump", None, name + " Pump"],
            prefix + "_Prec":     [None, "mdi:reload", None, name + " Recirculation"],
            prefix + "_Tpol":     [UnitOfTemperature.CELSIUS, "mdi:thermometer", SensorDeviceClass.TEMPERATURE, name + " Flow Target Temperature"],
            prefix + "_Tpol1":    [UnitOfTemperature.CELSIUS, "mdi:thermometer", SensorDeviceClass.TEMPERATURE, name + " Flow Measured Temperature"],
            prefix + "_Tsob":     [UnitOfTemperature.CELSIUS, "mdi:thermometer", SensorDeviceClass.TEMPERATURE, name + " Room Target Temperature"],
            prefix + "_Tsob1":    [UnitOfTemperature.CELSIUS, "mdi:thermometer", SensorDeviceClass.TEMPERATURE, name + " Room Measured Temperature"],
            prefix + "_zahP":     [None, "mdi:pump", None, name + " Pump Active"],
            prefix + "_misC":     [None, "mdi:pipe-valve", None, name + " Valve Closing"],
            prefix + "_misO":     [None, "mdi:pipe-valve", None, name + " Valve Opening"],
        }
        for param_id, sensor_data in items.items():
            if not WebBoilerGenericSensor._device_has_parameter(device, param_id):
                continue
            parameter = device.get_parameter(param_id)
            if parameter.get("used"):
                continue
            entities.append(WebBoilerGenericSensor(hass, device, sensor_data, parameter))
        return entities
