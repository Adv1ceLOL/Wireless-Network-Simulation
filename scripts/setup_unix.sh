#!/bin/bash

echo "=================================================================="
echo " Wireless Sensor Network Simulator - Unix Setup Script"
echo "=================================================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found! Please install Python 3.6 or higher."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS, you can install Python with:"
        echo "  brew install python"
        echo "or download from https://www.python.org/downloads/"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Linux, you can install Python with:"
        echo "  sudo apt-get install python3 python3-pip  # Debian/Ubuntu"
        echo "  sudo dnf install python3 python3-pip      # Fedora"
        echo "  sudo pacman -S python python-pip          # Arch Linux"
    fi
    
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$python_version < 3.6" | bc -l) )); then
    echo "You need Python 3.6 or higher."
    echo "Your current Python version is: $python_version"
    exit 1
fi

echo "Python version check passed."
echo ""

# Determine pip command
if command -v pip3 &> /dev/null; then
    PIP=pip3
elif command -v pip &> /dev/null; then
    PIP=pip
else
    echo "pip not found. Installing pip..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        python3 -m ensurepip
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get install python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S python-pip
        else
            python3 -m ensurepip
        fi
    fi
    
    if command -v pip3 &> /dev/null; then
        PIP=pip3
    elif command -v pip &> /dev/null; then
        PIP=pip
    else
        echo "Failed to install pip. Please install pip manually."
        exit 1
    fi
fi

# Create necessary directories
echo "Creating directory structure..."
mkdir -p output/visualizations
mkdir -p output/reports

# Install dependencies
echo "Installing required Python packages..."
$PIP install --upgrade pip
$PIP install matplotlib networkx pillow

# Run the dependency installation script
echo "Running dependency checks..."
python3 install_dependencies.py

# Run a simple test to verify installation
echo ""
echo "Running a simple test to verify installation..."
python3 tests/test_simple.py

echo ""
echo "=================================================================="
echo " Setup complete! "
echo "=================================================================="
echo ""
echo "To run the simulator, use: python3 simulation.py"
echo "For interactive mode, use: python3 simulation.py --interactive"
echo ""
echo "To run tests, use any of the following:"
echo "- python3 tests/test_simple.py"
echo "- python3 tests/test_simulator.py"
echo "- python3 tests/test_iterations.py"
echo ""
