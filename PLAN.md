# Implementation Plan

## Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Firmware    | Arduino C++ (ESP32 Arduino core)    |
| HTTP server | `WebServer.h` (built-in ESP32 lib)  |
| Web app     | Vanilla HTML/CSS/JS (single file)   |
| Build       | `arduino-cli` + GNU Make            |
| Test server | Python + FastAPI via `uv run`       |

---

## Phase 1 — Web App (`webapp/`)

**File**: `webapp/index.html`

Single self-contained HTML file (CSS and JS inline to simplify embedding).

UI elements:
- Password input field
- **Open** button → `POST /api/open`
- **Close** button → `POST /api/close`
- Status badge showing last action result
- Mobile-first, dark theme

Fetch pattern:
```js
async function sendCommand(action) {
  const res = await fetch(`/api/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: passwordInput.value })
  });
  const data = await res.json();
  // update status badge
}
```

---

## Phase 2 — Embed Script (`scripts/embed_webapp.py`)

Reads `webapp/index.html`, escapes it, and writes `esp32/web_app.h`:

```c
// Auto-generated — do not edit
#pragma once
const char INDEX_HTML[] PROGMEM = R"rawhtml(
  ... html content ...
)rawhtml";
```

Run automatically by `make build` before compilation.

---

## Phase 3 — ESP32 Firmware (`esp32/`)

### `config.h`
```c
#define WIFI_SSID       "your-ssid"
#define WIFI_PASSWORD   "your-wifi-password"
#define DOOR_PASSWORD   "your-door-password"
#define RELAY_PIN       26
#define RELAY_PULSE_MS  500
```

### `esp32.ino`

Startup sequence:
1. Connect to WiFi (blocking, retries every 500ms)
2. Print IP address to Serial
3. Register HTTP routes
4. Start WebServer

Routes:
- `GET /` → respond with `INDEX_HTML` (PROGMEM), `Content-Type: text/html`
- `POST /api/open` → validate password → pulse relay HIGH for `RELAY_PULSE_MS` ms → JSON `{"ok": true}`
- `POST /api/close` → validate password → set relay LOW → JSON `{"ok": true}`
- `GET /api/status` → JSON `{"door": "open"|"closed"}`
- Any other → 404 JSON

Password validation:
```cpp
// Parse JSON body, compare password field
// Return 401 JSON on mismatch
```

Relay pulse (open):
```cpp
digitalWrite(RELAY_PIN, HIGH);
delay(RELAY_PULSE_MS);
digitalWrite(RELAY_PIN, LOW);
```

---

## Phase 4 — Makefile

```makefile
BOARD   = esp32:esp32:esp32
PORT    = /dev/ttyUSB0
SKETCH  = esp32/esp32.ino

all: build

esp32/web_app.h: webapp/index.html scripts/embed_webapp.py
    python3 scripts/embed_webapp.py

build: esp32/web_app.h
    arduino-cli compile --fqbn $(BOARD) esp32/

upload: build
    arduino-cli upload -p $(PORT) --fqbn $(BOARD) esp32/

clean:
    rm -f esp32/web_app.h
    rm -rf esp32/build
```

---

## Phase 5 — Python Test Server (`server/main.py`)

Uses PEP 723 inline script dependencies (native `uv run` support):

```python
# /// script
# dependencies = ["fastapi", "uvicorn[standard]"]
# ///
```

Behaviour:
- Serves `webapp/index.html` at `GET /`
- Mocks `POST /api/open` and `POST /api/close` with password check
- Mocks `GET /api/status`
- Logs door commands to console (simulates relay toggle)
- Default port: `8000`

### `run.sh`
```bash
#!/usr/bin/env bash
set -e
uv run server/main.py
```

---

## Implementation Order

1. `esp32/config.h`
2. `webapp/index.html`
3. `scripts/embed_webapp.py`
4. `esp32/esp32.ino`
5. `Makefile`
6. `server/main.py`
7. `run.sh`

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| HTML embedding | PROGMEM C string | No SPIFFS setup needed, simpler for a single-file app |
| Auth method | Password in POST body (JSON) | Simple, sufficient for local WiFi only |
| Relay behavior | Pulse on Open, hold LOW on Close | Generic — works for both door strikes and magnetic locks |
| Test server | FastAPI + uv | Fast to set up, good DX, inline deps with `uv run` |
| Build tool | arduino-cli | CLI-native, easy Makefile integration |
