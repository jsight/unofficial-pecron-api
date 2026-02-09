# unofficial-pecron-api

Unofficial Python API client for **Pecron portable power stations**. Query battery level, power input/output, switch states, and more from the Pecron cloud.

> **Disclaimer:** This project is not affiliated with or endorsed by Pecron. It was reverse-engineered from the Pecron Android app for personal and home-automation use. Use at your own risk.

## Features

- Authenticate with the Pecron/Quectel cloud API (US, EU, CN regions)
- List all devices on your account
- Read live device properties: battery %, input/output wattage, AC/DC switches, UPS mode, charge/discharge time estimates, and more
- CLI tool with human-readable and JSON output modes
- Clean Python API for integration into other projects (e.g. Home Assistant)

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Pecron account with at least one device bound

## Installation

### With uv (recommended)

```bash
git clone https://github.com/jsightler/unofficial-pecron-api.git
cd unofficial-pecron-api
uv sync
```

### With pip

```bash
git clone https://github.com/jsightler/unofficial-pecron-api.git
cd unofficial-pecron-api
pip install .
```

## CLI Usage

The CLI is available as `pecron` after installation. With uv, prefix commands with `uv run`:

### List devices

```bash
uv run pecron devices
```

### Show device status

```bash
# All devices
uv run pecron status

# A specific device (substring match on name)
uv run pecron status --device E300LFP
```

Example output:

```
  E300LFP_D469 (E300LFP) [Online]
    Firmware:       WIFI01R13A01_OCPU_QTH_MCU_1.0.3
    Battery:        [||||||||||||||||||||] 98%
    Input Power:    2 W
    Output Power:   145 W
    Switches:       AC=ON, DC=OFF, UPS=ON
    Time to Empty:  1h 58m
    AC Output:      145 W @ 124 V / 60 Hz
    AC Input:       2 W
```

### JSON output

Every command supports `--json` for machine-readable output:

```bash
uv run pecron status --json
uv run pecron devices --json
```

### Dump raw API response

For debugging or discovering new fields:

```bash
uv run pecron raw
uv run pecron raw --device E300LFP
```

### Authentication options

Credentials can be provided three ways (in order of precedence):

1. **Command-line flags:**
   ```bash
   uv run pecron status --email user@example.com --password secret --region US
   ```

2. **Environment variables:**
   ```bash
   export PECRON_EMAIL="user@example.com"
   export PECRON_PASSWORD="secret"
   export PECRON_REGION="US"
   uv run pecron status
   ```

3. **Interactive prompt** (default if not provided above)

### All CLI options

```
usage: pecron [-h] [-r {CN,EU,US}] [-e EMAIL] [-p PASSWORD] [-d NAME]
              [--json] [-v] [--version]
              {devices,status,raw} ...

Options:
  -r, --region {CN,EU,US}   Cloud region (default: US)
  -e, --email EMAIL          Account email
  -p, --password PASSWORD    Account password
  -d, --device NAME          Filter by device name (substring match)
  --json                     Output as JSON
  -v, --verbose              Increase verbosity (-v info, -vv debug)
  --version                  Show version

Commands:
  devices    List all devices on the account
  status     Show device properties (battery, power, switches)
  raw        Dump raw business attributes as JSON
```

## Python API

```python
from unofficial_pecron_api import PecronAPI

with PecronAPI(region="US") as api:
    api.login("user@example.com", "password")

    for device in api.get_devices():
        props = api.get_device_properties(device)
        print(f"{device.device_name}: {props.battery_percentage}%")
        print(f"  Input: {props.total_input_power}W")
        print(f"  Output: {props.total_output_power}W")
        print(f"  AC: {'ON' if props.ac_switch else 'OFF'}")
```

### Key classes

**`PecronAPI(region="US")`** — Main client. Supports `"US"`, `"EU"`, `"CN"` regions.

| Method | Returns | Description |
|---|---|---|
| `login(email, password)` | `None` | Authenticate (stores token internally) |
| `get_devices()` | `list[Device]` | All devices on the account |
| `get_device_properties(device)` | `DeviceProperties` | Live battery/power/switch state |
| `get_device_info(device)` | `dict` | Raw device info |
| `close()` | `None` | Close HTTP session |

**`Device`** — A bound device.

| Field | Type | Description |
|---|---|---|
| `device_name` | `str` | e.g. `"E300LFP_D469"` |
| `product_name` | `str` | e.g. `"E300LFP"` |
| `product_key` | `str` | API identifier |
| `device_key` | `str` | API identifier |
| `online` | `bool` | Online status |
| `firmware_version` | `str \| None` | Populated after `get_device_properties()` |

**`DeviceProperties`** — Live device state.

| Field | Type | Description |
|---|---|---|
| `battery_percentage` | `int \| None` | 0-100 |
| `total_input_power` | `int \| None` | Watts |
| `total_output_power` | `int \| None` | Watts |
| `ac_switch` | `bool \| None` | AC output on/off |
| `dc_switch` | `bool \| None` | DC output on/off |
| `ups_status` | `bool \| None` | UPS mode on/off |
| `remain_charging_time` | `int \| None` | Minutes to full |
| `remain_discharging_time` | `int \| None` | Minutes to empty |
| `ac_output` | `dict \| None` | Voltage, power, PF, Hz |
| `dc_output` | `dict \| None` | Power |
| `ac_input` | `dict \| None` | Power |
| `dc_input` | `dict \| None` | Power |
| `raw` | `list[dict]` | Full `customizeTslInfo` for custom access |

Use `props.get_by_code("resource_code")` to access any property not covered by the typed fields.

## Supported Regions

| Region | API Endpoint |
|---|---|
| `US` | `iot-api.landecia.com` |
| `EU` | `iot-api.acceleronix.io` |
| `CN` | `iot-api.quectelcn.com` |

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/
```

## License

MIT
