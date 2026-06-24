#!/usr/bin/env bash
# Double-click this on a Mac to start the HW Lab.
# First run installs everything automatically; later runs start instantly.
set -e

# Work from the folder this script lives in, no matter where it's launched from.
cd "$(dirname "$0")"

# Make sure uv (our installer/runtime) is available.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "Setting up for the first time (installing uv)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

cd python-client

# Wait until the server is actually answering, then open the browser. The first
# run can take a few minutes while uv installs Python and the libraries, so we
# poll instead of guessing a fixed delay.
(
  for _ in $(seq 1 600); do
    if curl -sf -o /dev/null "http://localhost:8000/"; then
      open "http://localhost:8000"
      break
    fi
    sleep 1
  done
) >/dev/null 2>&1 &

echo ""
echo "Starting the HW Lab. Your browser will open automatically."
echo "Leave this window open while you work. Close it (or press Ctrl-C) to stop."
echo ""

# uv reads pyproject.toml, sets up Python + libraries on first run, then runs.
# --timeout-graceful-shutdown keeps saves snappy: the live video stream never
# ends on its own, so without this the auto-reload would wait on it for ages.
uv run uvicorn main:app --reload --port 8000 --timeout-graceful-shutdown 2
