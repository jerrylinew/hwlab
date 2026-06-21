"""Client for sending commands to the Seeed Studio XIAO ESP32C3.

Transport defaults to auto:
1. Try WiFi HTTP at http://192.168.4.1.
2. Fall back to USB serial, usually /dev/ttyACM0.

Optional environment overrides:
    XIAO_TRANSPORT=http|serial|auto
    XIAO_IP=192.168.4.1
    XIAO_SERIAL_PORT=/dev/ttyACM0
"""

import glob
import json
import os
import threading
import time

import requests

XIAO_IP = os.getenv("XIAO_IP", "192.168.4.1")
XIAO_PORT = int(os.getenv("XIAO_PORT", "80"))
XIAO_TRANSPORT = os.getenv("XIAO_TRANSPORT", "auto").lower()
XIAO_SERIAL_PORT = os.getenv("XIAO_SERIAL_PORT")
XIAO_SERIAL_BAUD = int(os.getenv("XIAO_SERIAL_BAUD", "115200"))
TIMEOUT_SECONDS = 1.0

_serial_lock = threading.Lock()
_serial_conn = None
_serial_port = None
_last_transport = "none"
_last_error = None


def send_command(command: str) -> bool:
    """Send a command to the XIAO. Returns True on success."""
    response = _request(command=str(command))
    return bool(response and response.get("ok"))


def get_status() -> dict | None:
    """GET the XIAO's status over HTTP or USB serial."""
    return _request(status=True)


def get_command() -> str | None:
    """Read the last command remembered by the XIAO."""
    status = get_status()
    if status and status.get("last_command") is not None:
        return str(status["last_command"])
    return None


def get_debug_info() -> dict:
    """Return transport details for the Vue diagnostics panel."""
    return {
        "configured_transport": XIAO_TRANSPORT,
        "last_transport": _last_transport,
        "last_error": _last_error,
        "http_url": f"http://{XIAO_IP}:{XIAO_PORT}",
        "serial_port": _serial_port or XIAO_SERIAL_PORT,
    }


def _request(command: str | None = None, status: bool = False) -> dict | None:
    if XIAO_TRANSPORT == "http":
        return _http_request(command=command, status=status)
    if XIAO_TRANSPORT == "serial":
        return _serial_request(command=command, status=status)

    response = _http_request(command=command, status=status)
    if response and response.get("ok"):
        return response
    return _serial_request(command=command, status=status)


def _http_request(command: str | None = None, status: bool = False) -> dict | None:
    global _last_error, _last_transport

    try:
        if command is not None:
            response = requests.post(
                f"http://{XIAO_IP}:{XIAO_PORT}/command",
                json={"command": command},
                timeout=TIMEOUT_SECONDS,
            )
        else:
            response = requests.get(
                f"http://{XIAO_IP}:{XIAO_PORT}/status",
                timeout=TIMEOUT_SECONDS,
            )

        if response.ok:
            _last_transport = "http"
            _last_error = None
            return response.json()

        _last_error = f"HTTP {response.status_code}"
    except requests.RequestException as exc:
        _last_error = f"HTTP failed: {exc}"
    return None


def _serial_request(command: str | None = None, status: bool = False) -> dict | None:
    global _last_error, _last_transport

    try:
        with _serial_lock:
            serial_conn = _get_serial_connection()
            if serial_conn is None:
                return None

            payload = {"command": command} if command is not None else {"status": True}
            serial_conn.write((json.dumps(payload) + "\n").encode("utf-8"))
            serial_conn.flush()

            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                line = serial_conn.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("ok"):
                    _last_transport = "serial"
                    _last_error = None
                    return data

            _last_error = "Serial timed out waiting for JSON status"
    except Exception as exc:
        _close_serial_connection()
        _last_error = f"Serial failed: {exc}"
    return None


def _get_serial_connection():
    global _last_error, _serial_conn, _serial_port

    if _serial_conn and _serial_conn.is_open:
        return _serial_conn

    try:
        import serial
    except ImportError:
        _last_error = "pyserial is not installed"
        return None

    port = XIAO_SERIAL_PORT or _find_serial_port()
    if not port:
        _last_error = "No XIAO serial port found"
        return None

    _serial_port = port
    _serial_conn = serial.Serial(port, XIAO_SERIAL_BAUD, timeout=0.25, write_timeout=0.5)
    _serial_conn.setDTR(False)
    _serial_conn.setRTS(False)
    time.sleep(1.5)
    _serial_conn.reset_input_buffer()
    return _serial_conn


def _close_serial_connection() -> None:
    global _serial_conn
    if _serial_conn:
        try:
            _serial_conn.close()
        except Exception:
            pass
    _serial_conn = None


def _find_serial_port() -> str | None:
    for pattern in ("/dev/ttyACM*", "/dev/ttyUSB*", "/dev/cu.usbmodem*", "/dev/cu.usbserial*"):
        ports = sorted(glob.glob(pattern))
        if ports:
            return ports[0]
    return None
