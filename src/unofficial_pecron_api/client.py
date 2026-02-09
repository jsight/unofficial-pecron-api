"""Pecron cloud API client.

Synchronous HTTP client for the Quectel IoE cloud platform used by Pecron
portable power stations.
"""

from __future__ import annotations

import logging
import uuid

import requests

from .auth import compute_signature, encrypt_password, generate_random
from .const import APP_ID, APP_SYSTEM_TYPE, APP_VERSION, REGIONS, Region
from .exceptions import AuthenticationError, DeviceNotFoundError, PecronAPIError
from .models import Device, DeviceProperties

_LOGGER = logging.getLogger(__name__)


class PecronAPI:
    """Client for the Pecron/Quectel cloud API."""

    def __init__(self, region: str | Region = "US") -> None:
        if isinstance(region, Region):
            region = region.value
        if region not in REGIONS:
            raise ValueError(f"Unknown region: {region}. Must be one of: {list(REGIONS.keys())}")
        self.region = region
        self._config = REGIONS[region]
        self._base_url = self._config["base_url"]
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._session = requests.Session()

    def _headers(self) -> dict[str, str]:
        """Build request headers matching wz1.java interceptor."""
        headers = {
            "X-Q-Language": "en",
            "quec-random-url": str(uuid.uuid4()),
            "app-info": "[HomeAssistant][Python][pecron-api][1]",
            "appId": APP_ID,
            "appVersion": APP_VERSION,
            "appSystemType": APP_SYSTEM_TYPE,
        }
        if self._access_token:
            headers["Authorization"] = self._access_token
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json_body: dict | None = None,
        form_data: dict | None = None,
    ) -> dict:
        """Make an authenticated HTTP request to the Quectel API."""
        url = self._base_url + path
        resp = self._session.request(
            method,
            url,
            params=params,
            json=json_body,
            data=form_data,
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        msg = data.get("msg", "")

        if code != 200:
            raise PecronAPIError(msg, code=code)

        return data.get("data")

    def login(self, email: str, password: str) -> None:
        """Authenticate with email and password.

        On success, stores the access/refresh tokens for subsequent requests.

        Raises:
            AuthenticationError: If login fails.
        """
        random_str = generate_random()
        encrypted_pwd = encrypt_password(password, random_str)
        signature = compute_signature(
            email, encrypted_pwd, random_str, self._config["user_domain_secret"]
        )

        body = {
            "email": email,
            "pwd": encrypted_pwd,
            "random": random_str,
            "userDomain": self._config["user_domain"],
            "signature": signature,
        }

        try:
            result = self._request(
                "POST",
                "/v2/enduser/enduserapi/emailPwdLogin",
                form_data=body,
            )
        except PecronAPIError as exc:
            raise AuthenticationError(exc.message, code=exc.code) from exc

        self._access_token = result["accessToken"]["token"]
        self._refresh_token = result["refreshToken"]["token"]
        _LOGGER.debug(
            "Login successful, token expires %s",
            result["accessToken"].get("expirationTime"),
        )

    def get_devices(self) -> list[Device]:
        """Get all devices bound to the account."""
        result = self._request("GET", "/v2/binding/enduserapi/userDeviceList")
        raw_list = result
        if isinstance(result, dict) and "list" in result:
            raw_list = result["list"]
        return [Device.from_api(d) for d in raw_list]

    def get_device_properties(self, device: Device) -> DeviceProperties:
        """Get current device properties (battery, power, switches, etc.).

        Raises:
            DeviceNotFoundError: If the device pk/dk is invalid.
        """
        try:
            result = self._request(
                "GET",
                "/v2/binding/enduserapi/getDeviceBusinessAttributes",
                params={"pk": device.product_key, "dk": device.device_key},
            )
        except PecronAPIError as exc:
            if exc.code and exc.code in (404, 4004):
                raise DeviceNotFoundError(exc.message, code=exc.code) from exc
            raise

        # Update device firmware info from deviceData if available
        device_data = result.get("deviceData") or {}
        if device_data.get("version"):
            device.firmware_version = device_data["version"]
        if device_data.get("mcuVersion"):
            device.mcu_version = device_data["mcuVersion"]

        tsl_info = result.get("customizeTslInfo") or []
        return DeviceProperties.from_api(tsl_info)

    def get_device_info(self, device: Device) -> dict:
        """Get raw device info dict."""
        return self._request(
            "GET",
            "/v2/binding/enduserapi/deviceInfo",
            params={"pk": device.product_key, "dk": device.device_key},
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self) -> PecronAPI:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
