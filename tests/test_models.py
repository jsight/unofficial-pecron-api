"""Tests for data model parsing."""

from unofficial_pecron_api.models import (
    CommandResult,
    Device,
    DeviceProperties,
    TslEnumValue,
    TslIntSpec,
    TslProperty,
)

SAMPLE_DEVICE_API = {
    "deviceName": "E300LFP_D469",
    "productKey": "p11u2Q",
    "deviceKey": "ACD9296AD469",
    "productName": "E300LFP",
    "onlineStatus": 1,
    "protocol": "MQTT",
    "signalStrength": -63,
    "lastConnTime": "2026-02-04 05:46:25",
    "sn": None,
}


SAMPLE_TSL_INFO = [
    {
        "abId": 1,
        "resourceCode": "battery_percentage",
        "name": "Battery power",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "INT",
        "resourceValce": "98",
        "createTime": "1770657750098",
    },
    {
        "abId": 2,
        "resourceCode": "remain_time",
        "name": "Discharging time",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "INT",
        "resourceValce": "118",
        "createTime": "1770657750098",
    },
    {
        "abId": 3,
        "resourceCode": "remain_charging_time",
        "name": "Full charging time",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "INT",
        "resourceValce": "60",
        "createTime": "1770657750098",
    },
    {
        "abId": 4,
        "resourceCode": "total_input_power",
        "name": "Input",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "INT",
        "resourceValce": "2",
        "createTime": "1770657750098",
    },
    {
        "abId": 5,
        "resourceCode": "total_output_power",
        "name": "Output",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "INT",
        "resourceValce": "145",
        "createTime": "1770657750098",
    },
    {
        "abId": 27,
        "resourceCode": "ups_status_hm",
        "name": "Ups status",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "BOOL",
        "resourceValce": "true",
        "createTime": "1770657750098",
    },
    {
        "abId": 38,
        "resourceCode": "dc_switch_hm",
        "name": "Dc switch",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "BOOL",
        "resourceValce": "false",
        "createTime": "1770657750098",
    },
    {
        "abId": 40,
        "resourceCode": "ac_switch_hm",
        "name": "Ac switch",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "BOOL",
        "resourceValce": "true",
        "createTime": "1770657750098",
    },
    {
        "abId": 31,
        "resourceCode": "ac_data_output_hm",
        "name": "AC",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "STRUCT",
        "resourceValce": (
            '{"ac_output_voltage":"124","ac_output_power":"145",'
            '"ac_output_pf":"1","ac_output_hz":"60"}'
        ),
        "createTime": "1770657750098",
    },
    {
        "abId": 30,
        "resourceCode": "dc_data_output_hm",
        "name": "DC",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "STRUCT",
        "resourceValce": '{"dc_output_power":"0"}',
        "createTime": "1770657750098",
    },
    {
        "abId": 29,
        "resourceCode": "ac_data_input_hm",
        "name": "AC",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "STRUCT",
        "resourceValce": '{"ac_power":"2"}',
        "createTime": "1770657750098",
    },
    {
        "abId": 28,
        "resourceCode": "dc_data_input_hm",
        "name": "DC/PV",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "STRUCT",
        "resourceValce": '{"dc_input_power":"0"}',
        "createTime": "1770657750098",
    },
    {
        "abId": 42,
        "resourceCode": "ac_charging_power_ios",
        "name": "Ac charging power",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "ENUM",
        "resourceValce": "2",
        "createTime": "1770657750098",
    },
    {
        "abId": 37,
        "resourceCode": "device_status_hm",
        "name": "Device status",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "ENUM",
        "resourceValce": "1",
        "createTime": "1770657750098",
    },
    {
        "abId": 41,
        "resourceCode": "eco_quite_mode_as",
        "name": "Eco silent mode",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "BOOL",
        "resourceValce": "false",
        "createTime": "1770657750098",
    },
    {
        "abId": 43,
        "resourceCode": "auto_light_flag_as",
        "name": "Auto-dim on idle",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "BOOL",
        "resourceValce": "true",
        "createTime": "1770657750098",
    },
    {
        "abId": 46,
        "resourceCode": "led_status_hm",
        "name": "Led",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "ENUM",
        "resourceValce": "0",
        "createTime": "1770657750098",
    },
    {
        "abId": 45,
        "resourceCode": "machine_screen_light_as",
        "name": "Machine screen brightness",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "ENUM",
        "resourceValce": "4",
        "createTime": "1770657750098",
    },
    {
        "abId": 34,
        "resourceCode": "noastime_io",
        "name": "No output auto-off time",
        "type": "PROPERTY",
        "subType": "RW",
        "dataType": "ENUM",
        "resourceValce": "0",
        "createTime": "1770657750098",
    },
    {
        "abId": 35,
        "resourceCode": "host_packet_data_jdb",
        "name": "Host electrical package details",
        "type": "PROPERTY",
        "subType": "R",
        "dataType": "STRUCT",
        "resourceValce": (
            '{"host_packet_current":"-10.7","host_packet_temp":"28",'
            '"host_packet_status":"0","host_packet_electric_percentage":"100",'
            '"host_packet_voltage":"20.3"}'
        ),
        "createTime": "1770657750098",
    },
]


class TestDevice:
    def test_from_api(self):
        dev = Device.from_api(SAMPLE_DEVICE_API)
        assert dev.device_name == "E300LFP_D469"
        assert dev.product_key == "p11u2Q"
        assert dev.device_key == "ACD9296AD469"
        assert dev.product_name == "E300LFP"
        assert dev.online is True
        assert dev.protocol == "MQTT"
        assert dev.signal_strength == -63

    def test_from_api_offline(self):
        data = {**SAMPLE_DEVICE_API, "onlineStatus": 0}
        dev = Device.from_api(data)
        assert dev.online is False

    def test_from_api_missing_fields(self):
        dev = Device.from_api({})
        assert dev.device_name == "Unknown"
        assert dev.product_key == ""
        assert dev.online is False


class TestDeviceProperties:
    def test_from_api_basic(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.battery_percentage == 98
        assert props.total_input_power == 2
        assert props.total_output_power == 145

    def test_from_api_switches(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.ac_switch is True
        assert props.dc_switch is False
        assert props.ups_status is True

    def test_from_api_times(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.remain_charging_time == 60
        assert props.remain_discharging_time == 118

    def test_from_api_charge_speed(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.ac_charge_speed == "2"

    def test_from_api_device_status(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.device_status == "1"
        assert props.eco_mode is False
        assert props.auto_dim is True
        assert props.led_status == "0"
        assert props.screen_brightness == "4"
        assert props.auto_off_time == "0"

    def test_from_api_eco_mode_f3000lfp_code(self):
        for value, expected in (("true", True), ("false", False)):
            props = DeviceProperties.from_api(
                [
                    {
                        "resourceCode": "eco_onoff_us",
                        "dataType": "BOOL",
                        "resourceValce": value,
                    }
                ]
            )
            assert props.eco_mode is expected

    def test_from_api_battery_pack(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.battery_pack is not None
        assert props.battery_pack["host_packet_temp"] == "28"
        assert props.battery_pack["host_packet_voltage"] == "20.3"
        assert props.battery_pack["host_packet_current"] == "-10.7"

    def test_from_api_struct_fields(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.ac_output == {
            "ac_output_voltage": "124",
            "ac_output_power": "145",
            "ac_output_pf": "1",
            "ac_output_hz": "60",
        }
        assert props.dc_output == {"dc_output_power": "0"}
        assert props.ac_input == {"ac_power": "2"}
        assert props.dc_input == {"dc_input_power": "0"}

    def test_raw_preserved(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert len(props.raw) == len(SAMPLE_TSL_INFO)

    def test_get_by_code(self):
        props = DeviceProperties.from_api(SAMPLE_TSL_INFO)
        assert props.get_by_code("battery_percentage") == "98"
        assert props.get_by_code("nonexistent") is None

    def test_empty_list(self):
        props = DeviceProperties.from_api([])
        assert props.battery_percentage is None
        assert props.raw == []

    def test_malformed_value_skipped(self):
        bad_tsl = [
            {
                "resourceCode": "battery_percentage",
                "resourceValce": "not_a_number",
                "dataType": "INT",
            }
        ]
        props = DeviceProperties.from_api(bad_tsl)
        assert props.battery_percentage is None


class TestCommandResult:
    def test_from_success_response(self):
        response = {
            "successList": [
                {
                    "data": {"productKey": "pk1", "deviceKey": "dk1"},
                    "ticket": "ticket_abc",
                }
            ],
            "failureList": [],
        }
        result = CommandResult.from_api(response, "pk1", "dk1")
        assert result.success is True
        assert result.ticket == "ticket_abc"
        assert result.error_message is None

    def test_from_failure_response(self):
        response = {
            "successList": [],
            "failureList": [
                {
                    "data": {"productKey": "pk1", "deviceKey": "dk1"},
                    "msg": "Device offline",
                }
            ],
        }
        result = CommandResult.from_api(response, "pk1", "dk1")
        assert result.success is False
        assert result.error_message == "Device offline"
        assert result.ticket is None

    def test_device_not_in_response(self):
        response = {
            "successList": [
                {"data": {"productKey": "other_pk", "deviceKey": "other_dk"}, "ticket": "t1"}
            ],
            "failureList": [],
        }
        result = CommandResult.from_api(response, "pk1", "dk1")
        assert result.success is False
        assert result.error_message == "Device not found in API response"

    def test_empty_lists(self):
        result = CommandResult.from_api({}, "pk1", "dk1")
        assert result.success is False

    def test_none_lists(self):
        result = CommandResult.from_api({"successList": None, "failureList": None}, "pk1", "dk1")
        assert result.success is False


class TestTslProperty:
    def test_from_api_read_only(self):
        prop = TslProperty.from_api(
            {
                "code": "battery_percentage",
                "name": "Battery power",
                "dataType": "INT",
                "subType": "R",
            }
        )
        assert prop.code == "battery_percentage"
        assert prop.name == "Battery power"
        assert prop.data_type == "INT"
        assert prop.sub_type == "R"
        assert prop.writable is False

    def test_from_api_read_write(self):
        prop = TslProperty.from_api(
            {
                "code": "ac_switch_hm",
                "name": "Ac switch",
                "dataType": "BOOL",
                "subType": "RW",
            }
        )
        assert prop.writable is True

    def test_from_api_write_only(self):
        prop = TslProperty.from_api(
            {
                "code": "some_command",
                "name": "Command",
                "dataType": "INT",
                "subType": "W",
            }
        )
        assert prop.writable is True

    def test_from_api_fallback_to_resource_code(self):
        prop = TslProperty.from_api(
            {
                "resourceCode": "dc_switch_hm",
                "name": "Dc switch",
                "dataType": "BOOL",
                "subType": "RW",
            }
        )
        assert prop.code == "dc_switch_hm"

    def test_from_api_missing_fields(self):
        prop = TslProperty.from_api({})
        assert prop.code == ""
        assert prop.name == ""
        assert prop.data_type == ""
        assert prop.sub_type == "R"
        assert prop.writable is False
        assert prop.enum_values == []
        assert prop.int_spec is None
        assert prop.enum_map == {}

    def test_from_api_enum_specs(self):
        prop = TslProperty.from_api(
            {
                "code": "ac_charging_power_ios",
                "name": "Ac charging power",
                "dataType": "ENUM",
                "subType": "RW",
                "specs": [
                    {"dataType": "ENUM", "name": "0", "value": "0"},
                    {"dataType": "ENUM", "name": "25", "value": "1"},
                    {"dataType": "ENUM", "name": "50", "value": "2"},
                    {"dataType": "ENUM", "name": "75", "value": "3"},
                    {"dataType": "ENUM", "name": "100", "value": "4"},
                ],
            }
        )
        assert len(prop.enum_values) == 5
        assert prop.enum_values[0] == TslEnumValue(value="0", name="0")
        assert prop.enum_values[4] == TslEnumValue(value="4", name="100")
        assert prop.enum_map == {"0": "0", "1": "25", "2": "50", "3": "75", "4": "100"}
        assert prop.int_spec is None

    def test_from_api_enum_specs_e3600(self):
        """Test enum specs for E3600LFP-style charge speed (1-10 = 10%-100%)."""
        specs = [{"dataType": "ENUM", "name": str(i * 10), "value": str(i)} for i in range(1, 11)]
        prop = TslProperty.from_api(
            {
                "code": "ac_charging_power_ios",
                "name": "Ac charging power",
                "dataType": "ENUM",
                "subType": "RW",
                "specs": specs,
            }
        )
        assert len(prop.enum_values) == 10
        assert prop.enum_map["1"] == "10"
        assert prop.enum_map["10"] == "100"

    def test_from_api_int_specs(self):
        prop = TslProperty.from_api(
            {
                "code": "total_output_power",
                "name": "Output",
                "dataType": "INT",
                "subType": "R",
                "specs": {"unit": "W", "min": "0", "max": "65535", "step": "1"},
            }
        )
        assert prop.enum_values == []
        assert prop.int_spec is not None
        assert prop.int_spec == TslIntSpec(min="0", max="65535", step="1", unit="W")

    def test_from_api_float_specs(self):
        prop = TslProperty.from_api(
            {
                "code": "ac_output_voltage",
                "name": "Ac output voltage",
                "dataType": "FLOAT",
                "subType": "R",
                "specs": {"unit": "V", "min": "0", "max": "65535", "step": "0.1"},
            }
        )
        assert prop.int_spec is not None
        assert prop.int_spec.unit == "V"
        assert prop.int_spec.step == "0.1"

    def test_from_api_specs_preserved_raw(self):
        raw_specs = [{"dataType": "ENUM", "name": "Off", "value": "0"}]
        prop = TslProperty.from_api(
            {
                "code": "noastime_io",
                "name": "Auto-off",
                "dataType": "ENUM",
                "subType": "RW",
                "specs": raw_specs,
            }
        )
        assert prop.specs is raw_specs
