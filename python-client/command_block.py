"""Tiny command blocks for student code.

Use these one-line helpers from main.py:

    send("thumbs_up")
    send_when(is_thumbs_up(hand), "thumbs_up")
    message = receive()
"""

import asyncio
import concurrent.futures
import json
import threading
import time
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from xiao_client import get_command, get_status, send_command

COMMAND_COOLDOWN_SECONDS = 2.0
GESTURE_CONFIRM_FRAMES = 3
RECEIVE_COOLDOWN_SECONDS = 0.5
SEND_TO_XIAO = True


def set_send_to_xiao(enabled: bool) -> None:
    """Choose whether student commands also go to the XIAO."""
    global SEND_TO_XIAO
    SEND_TO_XIAO = bool(enabled)


class CommandBlock:
    """Sends commands to the XIAO and Vue, and remembers commands from Vue."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._send_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._send_pool_stopped = False
        self._last_sent: dict[str, float] = {}
        self._seen_counts: dict[str, int] = {}
        self._last_received: str | None = None
        self._last_xiao_receive_check = 0.0
        self._last_xiao_command: str | None = None
        self._send_attempts = 0
        self._send_successes = 0
        self._last_sent_command: str | None = None
        self._last_sent_to_xiao = False
        self._lock = threading.Lock()

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        if self._send_pool_stopped:
            self._send_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            self._send_pool_stopped = False

    def stop(self) -> None:
        self._send_pool.shutdown(wait=False)
        self._send_pool_stopped = True

    def send(self, command: str) -> bool:
        """One-line block: send a command to the XIAO and the Vue app."""
        command = str(command)
        now = time.monotonic()
        if now - self._last_sent.get(command, 0.0) < COMMAND_COOLDOWN_SECONDS:
            return False

        self._last_sent[command] = now
        self._send_pool.submit(self._send_and_publish, command)
        return True

    def send_when(self, condition: bool, command: str) -> bool:
        """One-line gesture block: send after a gesture is seen for a few frames."""
        command = str(command)
        if condition:
            self._seen_counts[command] = self._seen_counts.get(command, 0) + 1
            if self._seen_counts[command] >= GESTURE_CONFIRM_FRAMES:
                return self.send(command)
            return False

        self._seen_counts[command] = 0
        return False

    def receive(self, default: str | None = None) -> str | None:
        """One-line block: read the last command from Vue or the XIAO."""
        with self._lock:
            if self._last_received is not None:
                return self._last_received

        command = self._receive_from_xiao()
        return command if command is not None else default

    def debug_status(self) -> dict:
        """Return connection and command status for the Vue diagnostics panel."""
        xiao_status = get_status() if SEND_TO_XIAO else None
        with self._lock:
            return {
                "python_ok": True,
                "send_to_xiao_enabled": SEND_TO_XIAO,
                "vue_clients": len(self._clients),
                "last_received_from_vue": self._last_received,
                "last_received_from_xiao": self._last_xiao_command,
                "last_sent_command": self._last_sent_command,
                "last_sent_to_xiao": self._last_sent_to_xiao,
                "send_attempts": self._send_attempts,
                "send_successes": self._send_successes,
                "xiao_connected": bool(xiao_status and xiao_status.get("ok")),
                "xiao_status": xiao_status,
            }

    async def websocket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)
        try:
            while True:
                self._remember_received(await websocket.receive_text())
        except WebSocketDisconnect:
            self._clients.discard(websocket)

    def _send_and_publish(self, command: str) -> None:
        send_to_xiao = SEND_TO_XIAO
        sent_ok = send_command(command) if send_to_xiao else False
        with self._lock:
            self._send_attempts += 1
            self._send_successes += int(sent_ok)
            self._last_sent_command = command
            self._last_sent_to_xiao = sent_ok
        self._publish(command, sent_ok, send_to_xiao)

    def _receive_from_xiao(self) -> str | None:
        if not SEND_TO_XIAO:
            return None

        now = time.monotonic()
        if now - self._last_xiao_receive_check < RECEIVE_COOLDOWN_SECONDS:
            return self._last_xiao_command

        self._last_xiao_receive_check = now
        self._last_xiao_command = get_command()
        return self._last_xiao_command

    def _publish(self, command: str, sent_to_xiao: bool, send_to_xiao: bool) -> None:
        if self._loop is None:
            return

        message = json.dumps(
            {
                "command": command,
                "sent_to_xiao": sent_to_xiao,
                "send_to_xiao_enabled": send_to_xiao,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

    async def _broadcast(self, message: str) -> None:
        for websocket in list(self._clients):
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(message)
                except Exception:
                    self._clients.discard(websocket)

    def _remember_received(self, message: str) -> None:
        send_now = False
        try:
            data = json.loads(message)
            command = str(data.get("command", message))
            send_now = bool(data.get("send_now", False))
        except json.JSONDecodeError:
            command = message

        with self._lock:
            self._last_received = command

        if send_now:
            self.send(command)


commands = CommandBlock()


def send(command: str) -> bool:
    """Send a command to the XIAO and show it in Vue."""
    return commands.send(command)


def send_when(condition: bool, command: str) -> bool:
    """Send a command when a gesture condition is true."""
    return commands.send_when(condition, command)


def receive(default: str | None = None) -> str | None:
    """Read the last command sent from Vue or remembered by the XIAO."""
    return commands.receive(default)
