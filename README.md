# phoneinfo

Powerful phone number information & OSINT tool for **Kali Linux** and **Termux** — validation, country, region, carrier, timezone, and location lookup.

## Features

| Feature | Source |
|---|---|
| ✅ Valid / possible number check | `phonenumbers` (Google libphonenumber) |
| 🌍 Country & region geocoding | `phonenumbers.geocoder` |
| 📍 Location area (from timezone) | built-in |
| 📱 Number type (mobile, VoIP, etc.) | `phonenumbers` |
| 🕐 Timezone(s) | `phonenumbers` |
| 📶 Local carrier (where available) | `phonenumbers.carrier` |
| 🌐 Live carrier & location | optional **numverify** API |
| 📊 JSON output | built-in |

## Installation

### Termux

```bash
pkg update && pkg upgrade -y
pkg install python -y
pip install -r requirements.txt
```

### Kali Linux

```bash
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install -r requirements.txt
```

## Usage

```bash
# Full offline lookup
python3 phoneinfo.py +14155552671

# Live carrier + location (get a free key at numverify.com)
NUMVERIFY_KEY=your_api_key_here python3 phoneinfo.py +14155552671 --remote

# JSON output (for scripts)
python3 phoneinfo.py +919876543210 --json

# Other language geocoding
python3 phoneinfo.py +14155552671 --lang hi
```

## Options

| Flag | Description |
|---|---|
| `--remote` | Query numverify API for carrier/location (needs `NUMVERIFY_KEY`) |
| `--json` | Machine-readable JSON output |
| `--lang` | Geocoder language (e.g. `hi`, `es`, `ar`) |

## Disclaimer

This tool is for educational and authorized use only. Only look up numbers you own or have explicit permission to check. Respect privacy laws in your country.
