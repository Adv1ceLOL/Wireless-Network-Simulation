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
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)"
if [ $? -ne 0 ]; then
    echo "You need Python 3.6 or higher."
    echo "Your current Python version is:"
    python3 --version
    exit 1
fi

# For macOS, suggest installing PyQt5 instead of tkinter
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "On macOS, PyQt5 is recommended over tkinter for GUI visualization."
    echo "Installing PyQt5 requires pip, which should be included with Python 3."
    echo ""
fi

# For Linux, suggest installing tkinter via package manager
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "On Linux, you may need to install tkinter via your package manager."
    echo "For Debian/Ubuntu: sudo apt-get install python3-tk"
    echo "For Fedora: sudo dnf install python3-tkinter"
    echo "For Arch Linux: sudo pacman -S tk"
    echo ""
    
    # Try to detect distribution and prompt for tkinter installation
    if command -v apt-get &> /dev/null; then
        read -p "Install python3-tk now? (y/n) " answer
        if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
            sudo apt-get install python3-tk
        fi
    elif command -v dnf &> /dev/null; then
        read -p "Install python3-tkinter now? (y/n) " answer
        if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
            sudo dnf install python3-tkinter
        fi
    elif command -v pacman &> /dev/null; then
        read -p "Install tk now? (y/n) " answer
        if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
            sudo pacman -S tk
        fi
    fi
    
    echo ""
fi

echo "Running dependency installer..."
echo ""
python3 install_dependencies.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error during dependency installation."
    echo "Please check the error messages above."
    exit 1
fi

echo ""
echo "=================================================================="
echo " Installation Complete!"
echo "=================================================================="
echo ""
echo "You can now run the simulator with:"
echo "  python3 simulation.py"
echo ""
echo "For interactive visualization:"
echo "  python3 simulation.py --interactive"
echo ""

# Make the simulation.py executable
chmod +x simulation.py
