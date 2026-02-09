#!/usr/bin/env python3
"""Minimal example: log in and print battery status for all devices.

Usage:
    uv run python examples/query_devices.py
"""

import getpass

from unofficial_pecron_api import PecronAPI

email = input("Email: ")
password = getpass.getpass("Password: ")

with PecronAPI(region="US") as api:
    api.login(email, password)

    for device in api.get_devices():
        props = api.get_device_properties(device)
        print(f"{device.device_name}: {props.battery_percentage}% battery")
