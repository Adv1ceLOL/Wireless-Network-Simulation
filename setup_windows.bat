@echo off
echo ==================================================================
echo  Wireless Sensor Network Simulator - Windows Setup Script
echo ==================================================================
echo.

:: Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python 3.6 or higher.
    echo Visit https://www.python.org/downloads/ to download and install Python.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo You need Python 3.6 or higher.
    echo Your current Python version is:
    python --version
    pause
    exit /b 1
)

echo Running dependency installer...
echo.
python install_dependencies.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error during dependency installation.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==================================================================
echo  Installation Complete!
echo ==================================================================
echo.
echo You can now run the simulator with:
echo   python simulation.py
echo.
echo For interactive visualization:
echo   python simulation.py --interactive
echo.
pause
