@echo off
echo Installing Smart Career Guidance dependencies...
cd /d "%~dp0"
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Running migrations...
python manage.py migrate
echo.
echo Done. Run "run.bat" to start the server.
