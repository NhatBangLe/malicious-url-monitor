# Malicious URL Monitor

A Windows-based security analysis tool that monitors system activity when visiting potentially malicious URLs. The tool captures registry changes, process activity, and network traffic during URL visits.

## Overview

This tool is designed to analyze the system-level impact of visiting a suspicious URL. It launches a browser to visit the target URL while simultaneously recording:
- Windows Registry changes
- Process/file system activity
- Network traffic

## System Requirements

- Windows OS with Administrator privileges
- [Sysinternals Process Monitor (Procmon)](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) - `C:\script\Procmon.exe`
- [NirSoft RegistryChangesView](https://www.nirsoft.net/utils/registry_changes_view.html) - `C:\script\RegistryChangesView.exe`
- [Wireshark](https://www.wireshark.org/) (with TShark) - `C:\Program Files\Wireshark\tshark.exe`
- Python 3.8+ is required

## Configuration

Create a `config.json` file in the same directory as `main.py`:

```json
{
    "script_path": "C:\\path\\to\\main.py",
    "target_url": "https://example.com/suspicious",
    "signal_file": "AUDIT_COMPLETED",
    "duration": 30,
    "output_path": "Z:\\",
    "regview_path": "C:\\script\\RegistryChangesView.exe",
    "procmon_path": "C:\\script\\Procmon.exe",
    "tshark_path": "C:\\Program Files\\Wireshark\\tshark.exe",
    "tshark_fields": ["frame.number", "ip.src", "ip.dst", "http.request.uri"],
    "interface_num": 1
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `script_path` | string | (required) | Path to the main script |
| `target_url` | string | (required) | The URL to visit and monitor |
| `signal_file` | string | `"AUDIT_COMPLETED"` | Filename created when audit finishes |
| `duration` | int | `30` | Monitoring duration in seconds |
| `output_path` | string | `"Z:\\"` | Output directory for results |
| `regview_path` | string | `RegistryChangesView.exe` | Path to RegistryChangesView |
| `procmon_path` | string | `Procmon.exe` | Path to Procmon |
| `tshark_path` | string | TShark in Program Files | Path to TShark |
| `tshark_fields` | list | Basic fields | TShark fields to export |
| `interface_num` | int | `1` | Network interface ID for capture |

## Usage

```bash
python main.py
```

The tool will:
1. Check for admin privileges (relaunches as admin if needed)
2. Wait for a valid `config.json` (up to 300 seconds)
3. Capture a registry baseline snapshot
4. Start Procmon and TShark monitoring
5. Launch browser to visit target URL
6. Wait for the specified duration
7. Stop all monitors and export results
8. Create a signal file when complete

## Output

Results are saved to a timestamped folder in `output_path`:
```
YYYYMMDD_HHMMSS/
├── reg_snapshot_before/     # Registry baseline snapshot
├── registry_diff.csv        # Registry changes during visit
├── procmon_log.CSV          # Process activity log
├── capture.pcapng           # Raw network capture
└── network_summary.csv      # Network traffic summary
```

## Architecture

```
main.py
├── helpers.py               # Logging, admin checks
├── data.py                  # ScriptArguments dataclass
└── controllers/
    ├── orchestrator.py      # Coordinates all monitoring
    ├── browser.py           # Chrome/Edge browser control
    ├── registry.py          # RegistryChangesView wrapper
    ├── procmon.py           # Procmon wrapper
    └── tshark.py            # TShark network capture wrapper
```

## Browser Support

- Google Chrome (default)
- Microsoft Edge

Both are launched with flags to disable security features for testing purposes (`--allow-running-insecure-content`, `--disable-web-security`, etc.).

## Notes

- Ensure all external tools (Procmon, RegistryChangesView, TShark) are accessible before running
- The browser will be closed automatically after the monitoring period
- A signal file is created upon completion for automation integration