"""Tests for PecronAPI client methods (mocked HTTP)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from unofficial_pecron_api import PecronAPI
from unofficial_pecron_api.exceptions import CommandError
from unofficial_pecron_api.models import Device


def _make_device(pk="p11u2Q", dk="ACD9296AD469"):
    return Device(
        device_name="E300LFP_D469",
        product_key=pk,
        device_key=dk,
        product_name="E300LFP",
        online=True,
        protocol="MQTT",
    )


def _mock_response(data, code=200):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"code": code, "msg": "success", "data": data}
    resp.raise_for_status = MagicMock()
    return resp


class TestSetDeviceProperty:
    def test_request_format(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [
                {"data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"}, "ticket": "t1"}
            ],
            "failureList": [],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_device_property(device, {"ac_switch_hm": True})

            call_args = api._session.request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1].endswith("/v2/binding/enduserapi/batchControlDevice")

            json_body = call_args[1]["json"]
            assert json_body["type"] == 2
            assert json_body["deviceList"][0]["productKey"] == "p11u2Q"
            assert json_body["deviceList"][0]["deviceKey"] == "ACD9296AD469"

            data_list = json.loads(json_body["data"])
            assert data_list == [{"ac_switch_hm": True}]

            assert result.success is True
            assert result.ticket == "t1"

    def test_multiple_properties(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [
                {"data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"}, "ticket": "t2"}
            ],
            "failureList": [],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_device_property(device, {"ac_switch_hm": True, "dc_switch_hm": False})

            json_body = api._session.request.call_args[1]["json"]
            data_list = json.loads(json_body["data"])
            assert {"ac_switch_hm": True} in data_list
            assert {"dc_switch_hm": False} in data_list
            assert result.success is True

    def test_failure_response(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [],
            "failureList": [
                {
                    "data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"},
                    "msg": "Device offline",
                }
            ],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_device_property(device, {"ac_switch_hm": True})
            assert result.success is False
            assert result.error_message == "Device offline"

    def test_api_error_raises_command_error(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        with patch.object(api._session, "request", return_value=_mock_response(None, code=500)):
            with pytest.raises(CommandError):
                api.set_device_property(device, {"ac_switch_hm": True})


class TestSetAcOutput:
    def test_on(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [
                {"data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"}, "ticket": "t3"}
            ],
            "failureList": [],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_ac_output(device, True)

            json_body = api._session.request.call_args[1]["json"]
            data_list = json.loads(json_body["data"])
            assert data_list == [{"ac_switch_hm": True}]
            assert result.success is True

    def test_off(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [
                {"data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"}, "ticket": "t4"}
            ],
            "failureList": [],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_ac_output(device, False)

            json_body = api._session.request.call_args[1]["json"]
            data_list = json.loads(json_body["data"])
            assert data_list == [{"ac_switch_hm": False}]
            assert result.success is True


class TestSetDcOutput:
    def test_on(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [
                {"data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"}, "ticket": "t5"}
            ],
            "failureList": [],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_dc_output(device, True)

            json_body = api._session.request.call_args[1]["json"]
            data_list = json.loads(json_body["data"])
            assert data_list == [{"dc_switch_hm": True}]
            assert result.success is True


class TestSetAcChargeSpeed:
    def test_sets_charge_speed(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        response_data = {
            "successList": [
                {"data": {"productKey": "p11u2Q", "deviceKey": "ACD9296AD469"}, "ticket": "t6"}
            ],
            "failureList": [],
        }

        with patch.object(api._session, "request", return_value=_mock_response(response_data)):
            result = api.set_ac_charge_speed(device, 2)

            json_body = api._session.request.call_args[1]["json"]
            data_list = json.loads(json_body["data"])
            assert data_list == [{"ac_charging_power_ios": 2}]
            assert result.success is True


class TestGetProductTsl:
    def test_parses_nested_tsl_json(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        tsl_response = {
            "tslJson": json.dumps(
                {
                    "properties": [
                        {
                            "code": "battery_percentage",
                            "name": "Battery power",
                            "dataType": "INT",
                            "subType": "R",
                            "specs": {"unit": "%", "min": "0", "max": "100", "step": "1"},
                        },
                        {
                            "code": "ac_switch_hm",
                            "name": "Ac switch",
                            "dataType": "BOOL",
                            "subType": "RW",
                        },
                    ]
                }
            )
        }

        with patch.object(api._session, "request", return_value=_mock_response(tsl_response)):
            props = api.get_product_tsl(device)
            assert len(props) == 2
            assert props[0].code == "battery_percentage"
            assert props[0].writable is False
            assert props[0].int_spec is not None
            assert props[0].int_spec.unit == "%"
            assert props[1].code == "ac_switch_hm"
            assert props[1].writable is True

    def test_parses_enum_specs(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        tsl_response = {
            "properties": [
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
                },
            ]
        }

        with patch.object(api._session, "request", return_value=_mock_response(tsl_response)):
            props = api.get_product_tsl(device)
            assert len(props) == 1
            p = props[0]
            assert len(p.enum_values) == 5
            assert p.enum_map == {"0": "0", "1": "25", "2": "50", "3": "75", "4": "100"}

    def test_parses_flat_properties(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        tsl_response = {
            "properties": [
                {
                    "code": "dc_switch_hm",
                    "name": "Dc switch",
                    "dataType": "BOOL",
                    "subType": "RW",
                },
            ]
        }

        with patch.object(api._session, "request", return_value=_mock_response(tsl_response)):
            props = api.get_product_tsl(device)
            assert len(props) == 1
            assert props[0].code == "dc_switch_hm"

    def test_parses_list_response(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        tsl_response = [
            {"code": "battery_percentage", "name": "Battery", "dataType": "INT", "subType": "R"},
        ]

        with patch.object(api._session, "request", return_value=_mock_response(tsl_response)):
            props = api.get_product_tsl(device)
            assert len(props) == 1

    def test_empty_response(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        with patch.object(api._session, "request", return_value=_mock_response({})):
            props = api.get_product_tsl(device)
            assert props == []
