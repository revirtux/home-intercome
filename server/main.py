# /// script
# dependencies = ["fastapi", "uvicorn[standard]"]
# ///
"""
Mock ESP32 server for local development.

Serves the web app from webapp/index.html and simulates the door
open/close/status endpoints, printing relay actions to the console.

Usage:
    uv run server/main.py
    uv run server/main.py --port 9000
"""

import argparse
import pathlib
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

# ---------------------------------------------------------------------------
# Config — must match esp32/config.h when testing end-to-end
# ---------------------------------------------------------------------------
DOOR_PASSWORD = "your-door-password"

WEBAPP_HTML = pathlib.Path("webapp/index.html")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(docs_url=None, redoc_url=None)

door_open = False


def _check_password(body: dict[str, Any]) -> bool:
    return body.get("password") == DOOR_PASSWORD


@app.get("/", response_class=HTMLResponse)
async def serve_webapp() -> HTMLResponse:
    if not WEBAPP_HTML.exists():
        return HTMLResponse("<h1>webapp/index.html not found</h1>", status_code=500)
    return HTMLResponse(WEBAPP_HTML.read_text(encoding="utf-8"))


@app.post("/api/open")
async def api_open(request: Request) -> JSONResponse:
    global door_open
    body = await request.json()
    if not _check_password(body):
        return JSONResponse({"ok": False, "error": "Wrong password"}, status_code=401)
    door_open = True
    print("[RELAY] >>> PULSE HIGH — door opened")
    return JSONResponse({"ok": True})


@app.post("/api/close")
async def api_close(request: Request) -> JSONResponse:
    global door_open
    body = await request.json()
    if not _check_password(body):
        return JSONResponse({"ok": False, "error": "Wrong password"}, status_code=401)
    door_open = False
    print("[RELAY] >>> LOW — door closed")
    return JSONResponse({"ok": True})


@app.get("/api/status")
async def api_status() -> JSONResponse:
    return JSONResponse({"door": "open" if door_open else "closed"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Mock ESP32 door server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    print(f"Mock server running at http://localhost:{args.port}")
    print(f"Door password: {DOOR_PASSWORD!r}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
