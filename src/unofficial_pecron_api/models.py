"""Data models for Pecron API responses."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

_LOGGER = logging.getLogger(__name__)


@dataclass
class Device:
    """A Pecron device from the device list API."""

    device_name: str
    product_key: str
    device_key: str
    product_name: str
    online: bool
    protocol: str
    firmware_version: str | None = None
    mcu_version: str | None = None
    device_sn: str | None = None
    signal_strength: int | None = None
    last_conn_time: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> Device:
        """Parse a device from the userDeviceList API response."""
        return cls(
            device_name=data.get("deviceName", "Unknown"),
            product_key=data.get("productKey", ""),
            device_key=data.get("deviceKey", ""),
            product_name=data.get("productName", ""),
            online=data.get("onlineStatus") == 1,
            protocol=data.get("protocol", ""),
            firmware_version=None,
            mcu_version=None,
            device_sn=data.get("sn"),
            signal_strength=data.get("signalStrength"),
            last_conn_time=data.get("lastConnTime"),
        )


@dataclass
class DeviceProperties:
    """Parsed device properties from getDeviceBusinessAttributes customizeTslInfo.

    Known resource codes and their meanings:
      - battery_percentage (INT): Battery level 0-100
      - total_input_power (INT): Total input power in watts
      - total_output_power (INT): Total output power in watts
      - ac_switch_hm (BOOL): AC output switch
      - dc_switch_hm (BOOL): DC output switch
      - ups_status_hm (BOOL): UPS mode active
      - remain_charging_time (INT): Minutes until fully charged
      - remain_time (INT): Minutes of discharge remaining
      - ac_data_output_hm (STRUCT): AC output voltage/power/pf/hz
      - dc_data_output_hm (STRUCT): DC output power
      - ac_data_input_hm (STRUCT): AC input power
      - dc_data_input_hm (STRUCT): DC/PV input power
    """

    battery_percentage: int | None = None
    total_input_power: int | None = None
    total_output_power: int | None = None
    ac_switch: bool | None = None
    dc_switch: bool | None = None
    ups_status: bool | None = None
    remain_charging_time: int | None = None
    remain_discharging_time: int | None = None
    ac_output: dict | None = None
    dc_output: dict | None = None
    ac_input: dict | None = None
    dc_input: dict | None = None
    raw: list[dict] = field(default_factory=list)

    @classmethod
    def from_api(cls, tsl_info: list[dict]) -> DeviceProperties:
        """Parse customizeTslInfo list into typed properties."""
        props = cls(raw=tsl_info)
        for item in tsl_info:
            code = item.get("resourceCode", "")
            value = item.get("resourceValce", "")  # Note: API typo
            data_type = item.get("dataType", "")
            try:
                props._apply(code, value, data_type)
            except (ValueError, TypeError, json.JSONDecodeError):
                _LOGGER.debug("Failed to parse property %s=%r", code, value)
        return props

    def _apply(self, code: str, value: str, data_type: str) -> None:
        """Apply a single property value by resource code."""
        if code == "battery_percentage":
            self.battery_percentage = int(value)
        elif code == "total_input_power":
            self.total_input_power = int(value)
        elif code == "total_output_power":
            self.total_output_power = int(value)
        elif code == "ac_switch_hm":
            self.ac_switch = value.lower() == "true"
        elif code == "dc_switch_hm":
            self.dc_switch = value.lower() == "true"
        elif code == "ups_status_hm":
            self.ups_status = value.lower() == "true"
        elif code == "remain_charging_time":
            self.remain_charging_time = int(value)
        elif code == "remain_time":
            self.remain_discharging_time = int(value)
        elif code == "ac_data_output_hm":
            self.ac_output = json.loads(value) if data_type == "STRUCT" else None
        elif code == "dc_data_output_hm":
            self.dc_output = json.loads(value) if data_type == "STRUCT" else None
        elif code == "ac_data_input_hm":
            self.ac_input = json.loads(value) if data_type == "STRUCT" else None
        elif code == "dc_data_input_hm":
            self.dc_input = json.loads(value) if data_type == "STRUCT" else None

    def get_by_code(self, resource_code: str) -> str | None:
        """Look up any property value by resource code from raw data."""
        for item in self.raw:
            if item.get("resourceCode") == resource_code:
                return item.get("resourceValce")
        return None


@dataclass
class CommandResult:
    """Result of a device command (set property) operation."""

    success: bool
    ticket: str | None = None
    error_message: str | None = None

    @classmethod
    def from_api(cls, response: dict, product_key: str, device_key: str) -> CommandResult:
        """Parse a batchControlDevice API response for a specific device."""
        for item in response.get("successList") or []:
            data = item.get("data") or {}
            if data.get("productKey") == product_key and data.get("deviceKey") == device_key:
                return cls(success=True, ticket=item.get("ticket"))

        for item in response.get("failureList") or []:
            data = item.get("data") or {}
            if data.get("productKey") == product_key and data.get("deviceKey") == device_key:
                return cls(success=False, error_message=item.get("msg"))

        return cls(success=False, error_message="Device not found in API response")


@dataclass
class TslProperty:
    """A device property definition from the Thing Specification Language model."""

    code: str
    name: str
    data_type: str
    sub_type: str
    writable: bool

    @classmethod
    def from_api(cls, data: dict) -> TslProperty:
        """Parse a single property from the productTSL API response."""
        sub_type = data.get("subType", "R")
        return cls(
            code=data.get("code", data.get("resourceCode", "")),
            name=data.get("name", ""),
            data_type=data.get("dataType", ""),
            sub_type=sub_type,
            writable=sub_type in ("RW", "W"),
        )
