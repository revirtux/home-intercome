# Home Intercom — ESP32 Door Controller

A web app embedded in an ESP32 that lets you open and close your building door from your local WiFi network.

## Overview

The ESP32 serves a small web app over HTTP. When you tap Open or Close in the browser, it sends an authenticated request to the ESP32, which pulses a relay connected to the door mechanism.

## Project Structure

```
home-intercome/
├── webapp/               # Web app source (HTML/CSS/JS)
│   └── index.html
├── esp32/                # ESP32 Arduino firmware
│   ├── esp32.ino         # Main sketch
│   ├── config.h          # WiFi credentials, door password, GPIO pin
│   └── web_app.h         # Auto-generated — do not edit (built by Makefile)
├── scripts/
│   └── embed_webapp.py   # Converts webapp/index.html → esp32/web_app.h
├── server/
│   └── main.py           # Python mock server for local testing (uv run)
├── Makefile              # Build, upload, clean
└── run.sh                # Start the Python test server
```

## Requirements

- **Hardware**: ESP32 board + relay module wired to a GPIO pin
- **Arduino CLI**: `arduino-cli` installed and configured
- **ESP32 Arduino core**: `esp32:esp32` board package installed
- **Python**: `uv` installed for running the test server

## Quick Start

### 1. Configure

Edit `esp32/config.h`:
```c
#define WIFI_SSID       "your-wifi-ssid"
#define WIFI_PASSWORD   "your-wifi-password"
#define DOOR_PASSWORD   "your-door-password"
#define RELAY_PIN       26
#define RELAY_PULSE_MS  500
```

### 2. Build & Upload

```bash
# Compile only
make build

# Compile + upload to ESP32
make upload PORT=/dev/ttyUSB0

# Clean build artifacts
make clean
```

### 3. Test Locally (without ESP32)

```bash
./run.sh
# Opens http://localhost:8000
```

## API Endpoints

| Method | Path         | Body                        | Description           |
|--------|--------------|-----------------------------|------------------------|
| GET    | `/`          | —                           | Serve the web app      |
| POST   | `/api/open`  | `{"password": "..."}` | Open the door          |
| POST   | `/api/close` | `{"password": "..."}` | Close the door         |
| GET    | `/api/status`| —                           | Get current door state |

## Hardware Wiring

```
ESP32 GPIO26 ──► Relay IN
ESP32 GND    ──► Relay GND
ESP32 3.3V   ──► Relay VCC

Relay COM    ──► Door opener common
Relay NO     ──► Door opener trigger
```

> Adjust `RELAY_PIN` in `config.h` to match your wiring.
