"""Command-line interface for the Pecron cloud API.

Usage:
    pecron devices                       # list all devices
    pecron status                        # show status of all devices
    pecron status --device E300LFP_D469  # show status of one device
    pecron set --ac on                   # turn AC output on
    pecron set --dc off --device E300    # turn DC output off for one device
    pecron set --charge-speed 600        # set AC charge speed
    pecron tsl --writable                # show writable properties
    pecron raw                           # dump raw business attributes JSON
"""

from __future__ import annotations

import argparse
import getpass
import json
import logging
import os
import sys

from . import PecronAPI, Region
from .exceptions import PecronAPIError
from .models import DeviceProperties


def _build_parser() -> argparse.ArgumentParser:
    # Shared arguments inherited by all subcommands
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-r",
        "--region",
        choices=[r.value for r in Region],
        default=os.environ.get("PECRON_REGION", "US"),
        help="Cloud region (default: $PECRON_REGION or US)",
    )
    common.add_argument(
        "-e",
        "--email",
        default=os.environ.get("PECRON_EMAIL"),
        help="Account email (default: $PECRON_EMAIL, or prompted)",
    )
    common.add_argument(
        "-p",
        "--password",
        default=os.environ.get("PECRON_PASSWORD"),
        help="Account password (default: $PECRON_PASSWORD, or prompted)",
    )
    common.add_argument(
        "-d",
        "--device",
        metavar="NAME",
        help="Filter to a specific device by name (substring match)",
    )
    common.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    common.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for info, -vv for debug)",
    )

    parser = argparse.ArgumentParser(
        prog="pecron",
        description="Query Pecron portable power station status via the cloud API.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.4.1",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("devices", parents=[common], help="List all devices on the account")
    sub.add_parser(
        "status", parents=[common], help="Show device properties (battery, power, switches)"
    )

    set_parser = sub.add_parser("set", parents=[common], help="Control device outputs (AC, DC)")
    set_parser.add_argument(
        "--ac",
        choices=["on", "off"],
        help="Turn AC output on or off",
    )
    set_parser.add_argument(
        "--dc",
        choices=["on", "off"],
        help="Turn DC output on or off",
    )
    set_parser.add_argument(
        "--charge-speed",
        metavar="LEVEL",
        help="Set AC charging power level (use 'pecron tsl --writable' to discover valid values)",
    )
    set_parser.add_argument(
        "--property",
        metavar="CODE",
        help="Set an arbitrary property by its TSL resource code",
    )
    set_parser.add_argument(
        "--value",
        help="Value for --property (required with --property)",
    )

    tsl_parser = sub.add_parser(
        "tsl", parents=[common], help="Show device property definitions from TSL"
    )
    tsl_parser.add_argument(
        "--writable",
        action="store_true",
        help="Show only writable (controllable) properties",
    )

    sub.add_parser("raw", parents=[common], help="Dump raw business attributes as JSON")

    return parser


def _configure_logging(verbosity: int) -> None:
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity >= 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )


def _get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve email and password from args, env, or interactive prompt."""
    email = args.email
    password = args.password

    if not email:
        try:
            email = input("Email: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.", file=sys.stderr)
            sys.exit(1)
    if not email:
        print("Error: email is required (use --email or $PECRON_EMAIL)", file=sys.stderr)
        sys.exit(1)

    if not password:
        try:
            password = getpass.getpass("Password: ")
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.", file=sys.stderr)
            sys.exit(1)
    if not password:
        print("Error: password is required (use --password or $PECRON_PASSWORD)", file=sys.stderr)
        sys.exit(1)

    return email, password


def _connect(args: argparse.Namespace) -> PecronAPI:
    """Create an authenticated PecronAPI client."""
    email, password = _get_credentials(args)
    api = PecronAPI(region=args.region)
    try:
        api.login(email, password)
    except PecronAPIError as exc:
        print(f"Login failed: {exc}", file=sys.stderr)
        sys.exit(1)
    return api


def _filter_devices(devices, name_filter: str | None):
    """Filter devices by substring match on device_name."""
    if not name_filter:
        return devices
    needle = name_filter.lower()
    matched = [d for d in devices if needle in d.device_name.lower()]
    if not matched:
        print(f"No device matching '{name_filter}' found.", file=sys.stderr)
        print(
            "Available: " + ", ".join(d.device_name for d in devices),
            file=sys.stderr,
        )
        sys.exit(1)
    return matched


def _cmd_devices(args: argparse.Namespace) -> None:
    with _connect(args) as api:
        devices = api.get_devices()
        if not devices:
            if args.json_output:
                print("[]")
            else:
                print("No devices found.")
            return

        if args.json_output:
            out = [
                {
                    "name": d.device_name,
                    "product": d.product_name,
                    "product_key": d.product_key,
                    "device_key": d.device_key,
                    "online": d.online,
                    "protocol": d.protocol,
                    "signal_strength": d.signal_strength,
                }
                for d in devices
            ]
            print(json.dumps(out, indent=2))
        else:
            print(f"Found {len(devices)} device(s):\n")
            for d in devices:
                status = "\033[32mOnline\033[0m" if d.online else "\033[31mOffline\033[0m"
                print(f"  {d.device_name}")
                print(f"    Product:  {d.product_name}")
                print(f"    Status:   {status}")
                print(f"    PK / DK:  {d.product_key} / {d.device_key}")
                if d.signal_strength is not None:
                    print(f"    Signal:   {d.signal_strength} dBm")
                print()


def _build_enum_map(api, dev, code: str) -> dict[str, str]:
    """Fetch TSL and return value->name map for an ENUM property, or empty dict."""
    try:
        tsl_props = api.get_product_tsl(dev)
        for p in tsl_props:
            if p.code == code and p.enum_values:
                return p.enum_map
    except PecronAPIError:
        pass
    return {}


def _cmd_status(args: argparse.Namespace) -> None:
    with _connect(args) as api:
        devices = _filter_devices(api.get_devices(), args.device)
        if not devices:
            if args.json_output:
                print("[]")
            else:
                print("No devices found.")
            return

        all_results = []
        for dev in devices:
            try:
                props = api.get_device_properties(dev)
            except PecronAPIError as exc:
                print(f"Error fetching {dev.device_name}: {exc}", file=sys.stderr)
                continue

            # Fetch TSL-based enum map for charge speed display
            charge_speed_map = _build_enum_map(api, dev, DeviceProperties.AC_CHARGE_SPEED_CODE)

            if args.json_output:
                entry = {
                    "device": dev.device_name,
                    "product": dev.product_name,
                    "online": dev.online,
                    "firmware": dev.firmware_version,
                    "battery_pct": props.battery_percentage,
                    "input_watts": props.total_input_power,
                    "output_watts": props.total_output_power,
                    "ac_switch": props.ac_switch,
                    "dc_switch": props.dc_switch,
                    "ups_mode": props.ups_status,
                    "eco_mode": props.eco_mode,
                    "auto_dim": props.auto_dim,
                    "ac_charge_speed": props.ac_charge_speed,
                    "device_status": props.device_status,
                    "led_status": props.led_status,
                    "screen_brightness": props.screen_brightness,
                    "auto_off_time": props.auto_off_time,
                    "charge_minutes": props.remain_charging_time,
                    "discharge_minutes": props.remain_discharging_time,
                    "ac_output": props.ac_output,
                    "dc_output": props.dc_output,
                    "ac_input": props.ac_input,
                    "dc_input": props.dc_input,
                    "battery_pack": props.battery_pack,
                }
                all_results.append(entry)
            else:
                _print_device_status(dev, props, charge_speed_map)

        if args.json_output:
            print(json.dumps(all_results, indent=2))


def _print_device_status(dev, props, charge_speed_map: dict[str, str] | None = None) -> None:
    """Pretty-print a single device's status to the terminal."""
    status = "\033[32mOnline\033[0m" if dev.online else "\033[31mOffline\033[0m"
    print(f"  {dev.device_name} ({dev.product_name}) [{status}]")

    if dev.firmware_version:
        print(f"    Firmware:       {dev.firmware_version}")

    if props.battery_percentage is not None:
        bar = _battery_bar(props.battery_percentage)
        print(f"    Battery:        {bar} {props.battery_percentage}%")
    if props.total_input_power is not None:
        print(f"    Input Power:    {props.total_input_power} W")
    if props.total_output_power is not None:
        print(f"    Output Power:   {props.total_output_power} W")

    switches = []
    if props.ac_switch is not None:
        switches.append(f"AC={'ON' if props.ac_switch else 'OFF'}")
    if props.dc_switch is not None:
        switches.append(f"DC={'ON' if props.dc_switch else 'OFF'}")
    if props.ups_status is not None:
        switches.append(f"UPS={'ON' if props.ups_status else 'OFF'}")
    if props.eco_mode is not None:
        switches.append(f"ECO={'ON' if props.eco_mode else 'OFF'}")
    if props.auto_dim is not None:
        switches.append(f"AutoDim={'ON' if props.auto_dim else 'OFF'}")
    if switches:
        print(f"    Switches:       {', '.join(switches)}")

    if props.device_status is not None:
        print(f"    Device Status:  {props.device_status}")
    if props.ac_charge_speed is not None:
        pct_map = charge_speed_map or {}
        name = pct_map.get(props.ac_charge_speed)
        label = f"{name}%" if name else props.ac_charge_speed
        print(f"    Charge Speed:   {label}")
    if props.led_status is not None:
        print(f"    LED:            {props.led_status}")
    if props.screen_brightness is not None:
        print(f"    Brightness:     {props.screen_brightness}")
    if props.auto_off_time is not None:
        print(f"    Auto-Off:       {props.auto_off_time}")

    if props.remain_charging_time is not None and props.remain_charging_time > 0:
        h, m = divmod(props.remain_charging_time, 60)
        print(f"    Time to Full:   {h}h {m:02d}m")
    if props.remain_discharging_time is not None and props.remain_discharging_time > 0:
        h, m = divmod(props.remain_discharging_time, 60)
        print(f"    Time to Empty:  {h}h {m:02d}m")

    if props.ac_output:
        v = props.ac_output.get("ac_output_voltage", "?")
        w = props.ac_output.get("ac_output_power", "?")
        hz = props.ac_output.get("ac_output_hz", "?")
        print(f"    AC Output:      {w} W @ {v} V / {hz} Hz")
    if props.dc_output:
        w = props.dc_output.get("dc_output_power", "?")
        print(f"    DC Output:      {w} W")
    if props.ac_input:
        w = props.ac_input.get("ac_power", "?")
        print(f"    AC Input:       {w} W")
    if props.dc_input:
        w = props.dc_input.get("dc_input_power", "?")
        print(f"    DC/PV Input:    {w} W")

    if props.battery_pack:
        temp = props.battery_pack.get("host_packet_temp", "?")
        current = props.battery_pack.get("host_packet_current", "?")
        voltage = props.battery_pack.get("host_packet_voltage", "?")
        try:
            current = f"{float(current):.1f}"
        except (ValueError, TypeError):
            pass
        try:
            voltage = f"{float(voltage):.1f}"
        except (ValueError, TypeError):
            pass
        print(f"    Battery Pack:   {voltage} V / {current} A / {temp} C")

    print()


def _battery_bar(pct: int, width: int = 20) -> str:
    """Render a small battery bar like [|||||||||...........] with color."""
    filled = round(pct / 100 * width)
    empty = width - filled
    if pct > 50:
        color = "\033[32m"  # green
    elif pct > 20:
        color = "\033[33m"  # yellow
    else:
        color = "\033[31m"  # red
    reset = "\033[0m"
    return f"[{color}{'|' * filled}{reset}{'.' * empty}]"


def _cmd_set(args: argparse.Namespace) -> None:
    # Build the properties dict from flags
    properties: dict = {}
    if args.ac is not None:
        properties["ac_switch_hm"] = args.ac == "on"
    if args.dc is not None:
        properties["dc_switch_hm"] = args.dc == "on"
    if args.charge_speed is not None:
        try:
            charge_val = json.loads(args.charge_speed)
        except (json.JSONDecodeError, ValueError):
            charge_val = args.charge_speed
        properties[DeviceProperties.AC_CHARGE_SPEED_CODE] = charge_val
    if args.property:
        if args.value is None:
            print("Error: --value is required when using --property", file=sys.stderr)
            sys.exit(1)
        # Try to parse the value as JSON (for booleans, numbers); fall back to string
        raw = args.value
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            parsed = raw
        properties[args.property] = parsed

    if not properties:
        print(
            "Error: at least one of --ac, --dc, --charge-speed, or --property is required",
            file=sys.stderr,
        )
        sys.exit(1)

    with _connect(args) as api:
        devices = _filter_devices(api.get_devices(), args.device)
        if not devices:
            print("No devices found.")
            return

        all_results = []
        exit_code = 0
        for dev in devices:
            try:
                result = api.set_device_property(dev, properties)
            except PecronAPIError as exc:
                print(f"Error sending command to {dev.device_name}: {exc}", file=sys.stderr)
                exit_code = 1
                continue

            if args.json_output:
                all_results.append(
                    {
                        "device": dev.device_name,
                        "success": result.success,
                        "ticket": result.ticket,
                        "error": result.error_message,
                    }
                )
            else:
                if result.success:
                    label = ", ".join(f"{k}={v}" for k, v in properties.items())
                    print(f"  {dev.device_name}: OK ({label})")
                else:
                    print(
                        f"  {dev.device_name}: FAILED - {result.error_message}",
                        file=sys.stderr,
                    )
                    exit_code = 1

        if args.json_output:
            print(json.dumps(all_results, indent=2))
        if exit_code:
            sys.exit(exit_code)


def _cmd_tsl(args: argparse.Namespace) -> None:
    with _connect(args) as api:
        devices = _filter_devices(api.get_devices(), args.device)
        if not devices:
            print("No devices found.")
            return

        all_results = []
        for dev in devices:
            try:
                tsl_props = api.get_product_tsl(dev)
            except PecronAPIError as exc:
                print(f"Error fetching TSL for {dev.device_name}: {exc}", file=sys.stderr)
                continue

            if args.writable:
                tsl_props = [p for p in tsl_props if p.writable]

            if args.json_output:
                props_out = []
                for p in tsl_props:
                    entry = {
                        "code": p.code,
                        "name": p.name,
                        "data_type": p.data_type,
                        "sub_type": p.sub_type,
                        "writable": p.writable,
                    }
                    if p.enum_values:
                        entry["enum_values"] = [
                            {"value": ev.value, "name": ev.name} for ev in p.enum_values
                        ]
                    if p.int_spec:
                        entry["int_spec"] = {
                            "min": p.int_spec.min,
                            "max": p.int_spec.max,
                            "step": p.int_spec.step,
                            "unit": p.int_spec.unit,
                        }
                    props_out.append(entry)
                all_results.append(
                    {
                        "device": dev.device_name,
                        "product": dev.product_name,
                        "properties": props_out,
                    }
                )
            else:
                label = "writable properties" if args.writable else "properties"
                print(f"  {dev.device_name} ({dev.product_name}) - {len(tsl_props)} {label}:\n")
                if tsl_props:
                    # Table header
                    print(f"    {'Code':<30s} {'Name':<20s} {'Type':<8s} {'Access'}")
                    print(f"    {'-' * 30} {'-' * 20} {'-' * 8} {'-' * 6}")
                    for p in tsl_props:
                        line = f"    {p.code:<30s} {p.name:<20s} {p.data_type:<8s} {p.sub_type}"
                        if p.enum_values:
                            vals = ", ".join(f"{ev.value}={ev.name}" for ev in p.enum_values)
                            line += f"  [{vals}]"
                        elif p.int_spec:
                            parts = []
                            if p.int_spec.min is not None:
                                parts.append(f"min={p.int_spec.min}")
                            if p.int_spec.max is not None:
                                parts.append(f"max={p.int_spec.max}")
                            if p.int_spec.unit:
                                parts.append(f"unit={p.int_spec.unit}")
                            if parts:
                                line += f"  [{', '.join(parts)}]"
                        print(line)
                else:
                    print("    (none)")
                print()

        if args.json_output:
            print(json.dumps(all_results, indent=2))


def _cmd_raw(args: argparse.Namespace) -> None:
    with _connect(args) as api:
        devices = _filter_devices(api.get_devices(), args.device)
        if not devices:
            print("{}" if args.json_output else "No devices found.")
            return

        all_raw = {}
        for dev in devices:
            try:
                result = api._request(
                    "GET",
                    "/v2/binding/enduserapi/getDeviceBusinessAttributes",
                    params={"pk": dev.product_key, "dk": dev.device_key},
                )
                all_raw[dev.device_name] = result
            except PecronAPIError as exc:
                all_raw[dev.device_name] = {"error": str(exc)}

        print(json.dumps(all_raw, indent=2, ensure_ascii=False))


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    _configure_logging(args.verbose)

    commands = {
        "devices": _cmd_devices,
        "status": _cmd_status,
        "set": _cmd_set,
        "tsl": _cmd_tsl,
        "raw": _cmd_raw,
    }
    commands[args.command](args)
