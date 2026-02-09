"""Constants and region configuration for the Pecron cloud API."""

from enum import Enum


class Region(Enum):
    """Supported Pecron cloud regions."""

    CN = "CN"
    EU = "EU"
    US = "US"


APP_ID = "633"
APP_VERSION = "1.9.0"
APP_SYSTEM_TYPE = "android"

REGIONS: dict[str, dict[str, str]] = {
    "CN": {
        "base_url": "https://iot-api.quectelcn.com",
        "ws_v2": "wss://iot-south.quectelcn.com:8443/ws/v2",
        "user_domain": "C.DM.5903.1",
        "user_domain_secret": "EufftRJSuWuVY7c6txzGifV9bJcfXHAFa7hXY5doXSn7",
    },
    "EU": {
        "base_url": "https://iot-api.acceleronix.io",
        "ws_v2": "wss://iot-south.acceleronix.io:8443/ws/v2",
        "user_domain": "C.DM.10351.1",
        "user_domain_secret": "FA5ZHXSka8y9GHvU91Hz1vWvaDSHE2mGW5B7bpn3fXTW",
    },
    "US": {
        "base_url": "https://iot-api.landecia.com",
        "ws_v2": "wss://iot-south.landecia.com:8443/ws/v2",
        "user_domain": "U.DM.10351.1",
        "user_domain_secret": "HARsQXfeex8vxyaPRAM8fyjqqVuH2uxAGQ3inJ8XxTiB",
    },
}
