# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-14

### Added
- Device control: turn AC and DC outputs on/off via `set_ac_output()`, `set_dc_output()`, and `set_device_property()`
- TSL property discovery via `get_product_tsl()` to find all available and writable device properties
- CLI `set` command with `--ac on/off`, `--dc on/off`, and `--property CODE --value VALUE` flags
- CLI `tsl` command with `--writable` filter to show controllable properties
- `CommandResult` model for device command responses
- `TslProperty` model for TSL property definitions
- `CommandError` exception for device command failures

### Fixed
- CLI flags (`--device`, `--json`, `-v`, etc.) now work correctly after subcommand names

## [0.1.0] - 2025-02-09

### Added
- Initial release of unofficial-pecron-api
- Support for Pecron/Quectel cloud authentication across US, EU, and CN regions
- Device listing and status querying functionality
- Live device property access: battery percentage, power input/output, switch states
- CLI tool with human-readable and JSON output modes
- Python API for integration into other projects
- Support for Home Assistant integration
- CLI commands: `devices`, `status`, `raw`
- Multiple authentication methods: CLI flags, environment variables, interactive prompts
