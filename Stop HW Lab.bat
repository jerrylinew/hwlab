@echo off
REM Double-click this on Windows to stop the HW Lab and turn the camera off.

REM Find whatever is listening on the lab's port (8000) and kill its whole
REM process tree (/T), so the reloader can't restart it.
set "FOUND="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr LISTENING ^| findstr ":8000"') do (
  taskkill /PID %%p /T /F >nul 2>nul
  set "FOUND=1"
)

echo.
if defined FOUND (
  echo The HW Lab is stopped and the camera is off.
) else (
  echo The HW Lab wasn't running.
)
echo You can close this window.
