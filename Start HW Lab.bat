@echo off
REM Double-click this on Windows to start the HW Lab.
REM First run installs everything automatically; later runs start instantly.

REM Work from the folder this script lives in.
cd /d "%~dp0"

REM Make sure uv (our installer/runtime) is available.
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul
if errorlevel 1 (
  echo Setting up for the first time ^(installing uv^)...
  powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

cd python-client

echo.
echo Starting the HW Lab. Your browser will open automatically.
echo Leave this window open while you work. Close it (or press Ctrl-C) to stop.
echo.

REM Wait until the server is actually answering, then open the browser. The first
REM run can take a few minutes while uv installs Python and the libraries, so we
REM poll instead of guessing a fixed delay.
start "" /b powershell -ExecutionPolicy Bypass -Command "$ErrorActionPreference='SilentlyContinue'; for($i=0;$i -lt 600;$i++){ try{ $c=New-Object Net.Sockets.TcpClient; $c.Connect('localhost',8000); $c.Close(); Start-Process 'http://localhost:8000'; break } catch { Start-Sleep -Seconds 1 } }"

REM uv reads pyproject.toml, sets up Python + libraries on first run, then runs.
REM --timeout-graceful-shutdown keeps saves snappy: the live video stream never
REM ends on its own, so without this the auto-reload would wait on it for ages.
uv run uvicorn main:app --reload --port 8000 --timeout-graceful-shutdown 2
