"""Client for sending commands to the Seeed Studio XIAO ESP32C3 webserver.

Set XIAO_IP to the IP printed by the XIAO's serial monitor on boot.
"""

import requests

XIAO_IP = "192.168.4.1"  # ESP32 AP default
XIAO_PORT = 80
TIMEOUT_SECONDS = 1.0


def send_command(command: str) -> bool:
    """POST a command to the XIAO. Returns True on success, False otherwise."""
    url = f"http://{XIAO_IP}:{XIAO_PORT}/command"
    try:
        resp = requests.post(url, json={"command": command}, timeout=TIMEOUT_SECONDS)
        return resp.ok
    except requests.RequestException:
        return False


def get_status() -> dict | None:
    """GET the XIAO's status. Returns the JSON dict or None on failure."""
    url = f"http://{XIAO_IP}:{XIAO_PORT}/status"
    try:
        resp = requests.get(url, timeout=TIMEOUT_SECONDS)
        if resp.ok:
            return resp.json()
    except requests.RequestException:
        pass
    return None
