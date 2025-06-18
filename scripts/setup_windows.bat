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

echo Python version check passed.
echo.

:: Create necessary directories
echo Creating directory structure...
if not exist output\visualizations mkdir output\visualizations
if not exist output\reports mkdir output\reports

:: Install dependencies
echo Installing required Python packages...
python -m pip install --upgrade pip
python -m pip install matplotlib networkx pillow

:: Run the dependency installation script
echo Running dependency checks...
python install_dependencies.py

:: Run a simple test to verify installation
echo.
echo Running a simple test to verify installation...
python tests\test_simple.py

echo.
echo ==================================================================
echo  Setup complete! 
echo ==================================================================
echo.
echo To run the simulator, use: python simulation.py
echo For interactive mode, use: python simulation.py --interactive
echo.
echo To run tests, use any of the following:
echo - python tests\test_simple.py
echo - python tests\test_simulator.py
echo - python tests\test_iterations.py
echo.
pause
