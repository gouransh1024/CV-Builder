@echo off
setlocal
cd /d "%~dp0"
echo =========================================================
echo  Smart Career Guidance - Automated Setup
echo =========================================================

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in PATH. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

REM Setup or verify .venv
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [*] Upgrading pip...
.\.venv\Scripts\python.exe -m pip install --upgrade pip

echo [*] Installing requirements.txt...
.\.venv\Scripts\pip.exe install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [*] Downloading NLTK corpora...
.\.venv\Scripts\python.exe -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True)"

echo [*] Applying database migrations...
.\.venv\Scripts\python.exe manage.py migrate

echo =========================================================
echo  Setup Completed Successfully!
echo  Double-click "run.bat" to start the application.
echo =========================================================
pause
