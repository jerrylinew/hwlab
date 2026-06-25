#!/usr/bin/env bash
# Double-click this on a Mac to stop the HW Lab and turn the camera off.
cd "$(dirname "$0")"

# Kill the lab server (both the reloader and its worker share this command line),
# so it stops for good instead of restarting itself.
if pkill -f "uvicorn main:app" 2>/dev/null; then
  sleep 1
fi

# Fallback: anything still listening on the lab's port.
remaining=$(lsof -nP -iTCP:8000 -sTCP:LISTEN -t 2>/dev/null)
if [ -n "$remaining" ]; then
  kill -9 $remaining 2>/dev/null
fi

echo ""
echo "The HW Lab is stopped and the camera is off."
echo "You can close this window."
