"""Tiny helper for sending commands to a Seeed Studio XIAO webserver.

Fill in XIAO_IP with the IP address printed by your XIAO's serial monitor
when it connects to WiFi (e.g. "192.168.1.42").
"""

import requests

XIAO_IP = "192.168.1.42"  # TODO: replace with your XIAO's IP address
XIAO_PORT = 80
TIMEOUT_SECONDS = 1.0


def send_command(command: str) -> bool:
    """POST a JSON command to the XIAO webserver.

    Returns True if the request succeeded, False otherwise (e.g. the
    XIAO is offline or XIAO_IP hasn't been set up yet). Failures are
    swallowed so the OpenCV loop never crashes because of the network.
    """
    url = f"http://{XIAO_IP}:{XIAO_PORT}/command"
    try:
        response = requests.post(url, json={"command": command}, timeout=TIMEOUT_SECONDS)
        return response.ok
    except requests.RequestException:
        return False
