@echo off
cd /d "%~dp0"
echo.
echo ============================================
echo   Smart Career Guidance - Network Mode
echo ============================================
echo.
echo Finding your local IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%
echo.
echo Your local IP: %IP%
echo.
echo Starting server on all interfaces...
echo.
echo Access from this computer:
echo   http://127.0.0.1:8000/
echo.
echo Access from other devices on same Wi-Fi:
echo   http://%IP%:8000/
echo.
echo Press Ctrl+C to stop the server.
echo ============================================
echo.
python manage.py runserver 0.0.0.0:8000
