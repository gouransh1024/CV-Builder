@echo off
setlocal
cd /d "%~dp0"

echo =========================================================
echo  Starting Smart Career Guidance System
echo =========================================================

REM Determine Python executable
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.\.venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

echo [*] Using Python: %PY_CMD%
echo [*] Server URL: http://127.0.0.1:8000/
echo [*] Press Ctrl+C in this terminal window to stop the server.
echo.

start "" "http://127.0.0.1:8000/"
%PY_CMD% manage.py runserver 127.0.0.1:8000
