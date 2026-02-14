"""Tests for data model parsing."""

from unofficial_pecron_api.models import CommandResult, Device, DeviceProperties, TslProperty

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
