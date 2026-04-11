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
      - eco_quite_mode_as (BOOL): Eco silent mode
      - auto_light_flag_as (BOOL): Auto-dim on idle
      - remain_charging_time (INT): Minutes until fully charged (see known issue below)
      - remain_time (INT): Minutes of discharge remaining (see known issue below)
      - ac_charging_power_ios (ENUM): AC charging power level (model-dependent; use TSL specs)
      - device_status_hm (ENUM): Device status code
      - led_status_hm (ENUM): LED control
      - machine_screen_light_as (ENUM): Screen brightness level
      - noastime_io (ENUM): No-output auto-off timer
      - ac_data_output_hm (STRUCT): AC output voltage/power/pf/hz
      - dc_data_output_hm (STRUCT): DC output power
      - ac_data_input_hm (STRUCT): AC input power
      - dc_data_input_hm (STRUCT): DC/PV input power
      - host_packet_data_jdb (STRUCT): Battery pack details (current/temp/voltage/status)

    Note: The ac_charging_power_ios code was discovered on the E300LFP.
    Other device models may use a different code — use ``pecron tsl --writable``
    to check.

    Known issue: The Pecron API returns identical values for ``remain_charging_time``
    and ``remain_time``. Both fields reflect the current device state — when
    discharging, both report time-to-empty; when charging, both report time-to-full.
    Only one value is meaningful at a given time. This is a Pecron API/firmware bug,
    not a bug in this library. See https://github.com/jsight/unofficial-pecron-api/issues/1
    """

    #: Resource code used for the AC charging power property. Override this
    #: class attribute if your device uses a different code (discover via TSL).
    AC_CHARGE_SPEED_CODE: str = "ac_charging_power_ios"

    battery_percentage: int | None = None
    total_input_power: int | None = None
    total_output_power: int | None = None
    ac_switch: bool | None = None
    dc_switch: bool | None = None
    ups_status: bool | None = None
    eco_mode: bool | None = None
    auto_dim: bool | None = None
    remain_charging_time: int | None = None
    remain_discharging_time: int | None = None
    ac_charge_speed: str | None = None
    device_status: str | None = None
    led_status: str | None = None
    screen_brightness: str | None = None
    auto_off_time: str | None = None
    ac_output: dict | None = None
    dc_output: dict | None = None
    ac_input: dict | None = None
    dc_input: dict | None = None
    battery_pack: dict | None = None
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
        elif code == "eco_quite_mode_as":
            self.eco_mode = value.lower() == "true"
        elif code == "auto_light_flag_as":
            self.auto_dim = value.lower() == "true"
        elif code == "remain_charging_time":
            self.remain_charging_time = int(value)
        elif code == "remain_time":
            self.remain_discharging_time = int(value)
        elif code == self.AC_CHARGE_SPEED_CODE:
            self.ac_charge_speed = value
        elif code == "device_status_hm":
            self.device_status = value
        elif code == "led_status_hm":
            self.led_status = value
        elif code == "machine_screen_light_as":
            self.screen_brightness = value
        elif code == "noastime_io":
            self.auto_off_time = value
        elif code == "ac_data_output_hm":
            self.ac_output = json.loads(value) if data_type == "STRUCT" else None
        elif code == "dc_data_output_hm":
            self.dc_output = json.loads(value) if data_type == "STRUCT" else None
        elif code == "ac_data_input_hm":
            self.ac_input = json.loads(value) if data_type == "STRUCT" else None
        elif code == "dc_data_input_hm":
            self.dc_input = json.loads(value) if data_type == "STRUCT" else None
        elif code == "host_packet_data_jdb":
            self.battery_pack = json.loads(value) if data_type == "STRUCT" else None

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
class TslEnumValue:
    """A single enum option from a TSL property spec."""

    value: str
    name: str

    def __repr__(self) -> str:
        return f"TslEnumValue(value={self.value!r}, name={self.name!r})"


@dataclass
class TslIntSpec:
    """Numeric range spec for INT/FLOAT TSL properties."""

    min: str | None = None
    max: str | None = None
    step: str | None = None
    unit: str | None = None


@dataclass
class TslProperty:
    """A device property definition from the Thing Specification Language model.

    The ``specs`` field captures the raw ``specs`` object from the API.

    For convenience, parsed specs are available via typed accessors:

    * ``enum_values`` — for ENUM properties, a list of :class:`TslEnumValue`
      (value/name pairs) derived from specs.
    * ``int_spec`` — for INT/FLOAT properties, a :class:`TslIntSpec` with
      min/max/step/unit.
    * ``enum_map`` — shortcut dict mapping API value -> display name for ENUMs.
    """

    code: str
    name: str
    data_type: str
    sub_type: str
    writable: bool
    specs: list | dict | None = field(default=None, repr=False)
    enum_values: list[TslEnumValue] = field(default_factory=list)
    int_spec: TslIntSpec | None = None

    @property
    def enum_map(self) -> dict[str, str]:
        """Map of API value -> display name for ENUM properties.

        Returns an empty dict for non-ENUM properties.
        """
        return {ev.value: ev.name for ev in self.enum_values}

    @classmethod
    def from_api(cls, data: dict) -> TslProperty:
        """Parse a single property from the productTSL API response."""
        sub_type = data.get("subType", "R")
        raw_specs = data.get("specs")
        enum_values: list[TslEnumValue] = []
        int_spec: TslIntSpec | None = None
        data_type = data.get("dataType", "")

        if isinstance(raw_specs, list) and data_type == "ENUM":
            for item in raw_specs:
                if isinstance(item, dict) and "value" in item:
                    enum_values.append(TslEnumValue(value=item["value"], name=item.get("name", "")))
        elif isinstance(raw_specs, dict) and data_type in ("INT", "FLOAT"):
            int_spec = TslIntSpec(
                min=raw_specs.get("min"),
                max=raw_specs.get("max"),
                step=raw_specs.get("step"),
                unit=raw_specs.get("unit"),
            )

        return cls(
            code=data.get("code", data.get("resourceCode", "")),
            name=data.get("name", ""),
            data_type=data_type,
            sub_type=sub_type,
            writable=sub_type in ("RW", "W"),
            specs=raw_specs,
            enum_values=enum_values,
            int_spec=int_spec,
        )
