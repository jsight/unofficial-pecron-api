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

            form_data = call_args[1]["data"]
            assert "json" in form_data
            parsed = json.loads(form_data["json"])
            assert parsed["type"] == 0
            assert parsed["deviceList"][0]["productKey"] == "p11u2Q"
            assert parsed["deviceList"][0]["deviceKey"] == "ACD9296AD469"

            data_list = json.loads(parsed["data"])
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
            result = api.set_device_property(
                device, {"ac_switch_hm": True, "dc_switch_hm": False}
            )

            form_data = api._session.request.call_args[1]["data"]
            data_list = json.loads(json.loads(form_data["json"])["data"])
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

        with patch.object(
            api._session, "request", return_value=_mock_response(None, code=500)
        ):
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

            form_data = api._session.request.call_args[1]["data"]
            data_list = json.loads(json.loads(form_data["json"])["data"])
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

            form_data = api._session.request.call_args[1]["data"]
            data_list = json.loads(json.loads(form_data["json"])["data"])
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

            form_data = api._session.request.call_args[1]["data"]
            data_list = json.loads(json.loads(form_data["json"])["data"])
            assert data_list == [{"dc_switch_hm": True}]
            assert result.success is True


class TestGetProductTsl:
    def test_parses_nested_tsl_json(self):
        api = PecronAPI(region="US")
        api._access_token = "test_token"
        device = _make_device()

        tsl_response = {
            "tslJson": json.dumps({
                "properties": [
                    {
                        "code": "battery_percentage",
                        "name": "Battery power",
                        "dataType": "INT",
                        "subType": "R",
                    },
                    {
                        "code": "ac_switch_hm",
                        "name": "Ac switch",
                        "dataType": "BOOL",
                        "subType": "RW",
                    },
                ]
            })
        }

        with patch.object(api._session, "request", return_value=_mock_response(tsl_response)):
            props = api.get_product_tsl(device)
            assert len(props) == 2
            assert props[0].code == "battery_percentage"
            assert props[0].writable is False
            assert props[1].code == "ac_switch_hm"
            assert props[1].writable is True

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
