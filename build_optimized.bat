@echo off
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================================
echo Building Optimized Simple Phantast App (EXE)
echo ============================================================
echo.

:: 1. Create temporary build environment
if not exist ".venv_build" (
    echo Creating virtual environment for clean build...
    python -m venv .venv_build
)

:: 2. Activate environment
call .venv_build\Scripts\activate.bat

:: 3. Install Requirements
echo Installing minimal dependencies...
pip install -r requirements_build.txt

:: 4. Build
echo Building with minimal environment...
:: --onefile: Bundle everything
:: --noconsole: Hide console
:: --exclude-module: Explicitly exclude heavy/unused libs if present in env (just in case)
python -m PyInstaller --noconsole --onefile --clean ^
    --name "SimplePhantast_Optimized" ^
    --exclude-module matplotlib ^
    --exclude-module tkinter ^
    --exclude-module torch ^
    --exclude-module tensorflow ^
    --exclude-module pandas ^
    --add-data "phantast_confluency_corrected.py;." ^
    src/gui/simple_app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Build Failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ============================================================
echo Build Complete!
echo Executable is in: dist\SimplePhantast_Optimized.exe
echo ============================================================
echo.
pause
