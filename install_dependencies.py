#!/usr/bin/env python3
"""
Wireless Network Simulator - Dependency Installer
------------------------------------------------
This script checks for and installs all required dependencies for the 
Wireless Network Simulator project.
"""

import os
import sys
import platform
import subprocess
import importlib.util
import argparse

# Set up command line arguments
parser = argparse.ArgumentParser(description='Install dependencies for Wireless Network Simulator')
parser.add_argument('--no-interactive', action='store_true', 
                    help='Install without interactive backend dependencies')
parser.add_argument('--force', action='store_true', 
                    help='Force reinstallation of dependencies')
args = parser.parse_args()

# Define colors for better readability
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Disable colors if on Windows without ANSI support
if platform.system() == 'Windows' and not os.environ.get('ANSICON'):
    for attr in dir(Colors):
        if not attr.startswith('__'):
            setattr(Colors, attr, '')

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}")

def print_step(text):
    """Print a step in the installation process."""
    print(f"{Colors.BLUE}→ {text}{Colors.ENDC}")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}! {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def is_package_installed(package_name):
    """Check if a Python package is installed."""
    if package_name == 'tkinter':
        # Special handling for tkinter
        try:
            import tkinter
            return True
        except ImportError:
            return False
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name, pip_name=None):
    """Install a Python package using pip."""
    if pip_name is None:
        pip_name = package_name
    
    if is_package_installed(package_name) and not args.force:
        print_success(f"{package_name} is already installed")
        return True
    
    try:
        print_step(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "--upgrade"], 
                               stdout=subprocess.PIPE if not args.force else None)
        print_success(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install {package_name}: {e}")
        return False

def get_system_package_manager_command():
    """Get the appropriate package manager command for the current system."""
    if platform.system() == 'Linux':
        # Try to detect the Linux distribution
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = dict([line.strip().split('=', 1) for line in f if '=' in line])
            
            if os_info.get('ID', '').lower() in ['debian', 'ubuntu', 'mint']:
                return 'sudo apt-get install'
            elif os_info.get('ID', '').lower() in ['fedora', 'centos', 'rhel']:
                return 'sudo dnf install'
            elif os_info.get('ID', '').lower() in ['arch', 'manjaro']:
                return 'sudo pacman -S'
            elif os_info.get('ID', '').lower() in ['opensuse']:
                return 'sudo zypper install'
        except:
            pass
        
        # Default for Linux
        return 'sudo apt-get install'
    
    elif platform.system() == 'Darwin':  # macOS
        return 'brew install'
    
    return None  # No system package manager for Windows

def check_system_dependencies():
    """Check and provide instructions for system-level dependencies."""
    print_header("Checking System Dependencies")
    
    # Dictionary mapping Python package name to system package name
    system_dependencies = {}
    
    if platform.system() == 'Linux':
        system_dependencies = {
            'tkinter': 'python3-tk',
            'PyQt5': 'python3-pyqt5'
        }
    elif platform.system() == 'Darwin':  # macOS
        system_dependencies = {
            'tkinter': 'python-tk',
            'PyQt5': 'pyqt5'
        }
    
    # Windows usually has these bundled with Python, or they're pure Python packages
    
    pkg_manager_cmd = get_system_package_manager_command()
    if pkg_manager_cmd and system_dependencies:
        missing_deps = []
        for pkg_name in system_dependencies:
            if not is_package_installed(pkg_name):
                missing_deps.append(system_dependencies[pkg_name])
        
        if missing_deps:
            print_warning("Some system dependencies may be missing")
            print(f"To install them, you may need to run:")
            print(f"    {pkg_manager_cmd} {' '.join(missing_deps)}")
            print("Note: This might require administrator privileges")

def install_core_dependencies():
    """Install core dependencies required for the simulator."""
    print_header("Installing Core Dependencies")
    
    core_deps = [
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('networkx', 'networkx'),
        ('Pillow', 'pillow')  # PIL
    ]
    
    success = True
    for package_name, pip_name in core_deps:
        if not install_package(package_name, pip_name):
            success = False
    
    return success

def install_gui_dependencies():
    """Install GUI backend dependencies for interactive visualization."""
    if args.no_interactive:
        print_warning("Skipping GUI dependencies as requested")
        return True
    
    print_header("Installing GUI Dependencies for Interactive Visualization")
    
    # Try to install platform-specific GUI backends
    if platform.system() == 'Windows':
        # tkinter should be included with Python on Windows
        # Try PyQt5 as fallback
        if not is_package_installed('tkinter'):
            print_warning("tkinter not found, which should be included with Python on Windows")
            print_step("Attempting to install PyQt5 as an alternative...")
            install_package('PyQt5', 'PyQt5')
    
    elif platform.system() == 'Darwin':  # macOS
        # Try the macOS-specific backend first, then PyQt5
        install_package('PyQt5', 'PyQt5')
    
    else:  # Linux
        # Try tkinter, but this often needs system packages
        if not is_package_installed('tkinter'):
            print_warning("tkinter not found")
            print_warning("On Linux, you may need to install the python3-tk package using your system's package manager")
            print_step("Attempting to install PyQt5 as an alternative...")
            install_package('PyQt5', 'PyQt5')
    
    # Check if we have at least one GUI backend available
    has_gui = any([
        is_package_installed('tkinter'),
        is_package_installed('PyQt5'),
        is_package_installed('PyQt4'),
        is_package_installed('wx')
    ])
    
    if has_gui:
        print_success("At least one GUI backend is available")
    else:
        print_warning("No GUI backends are available. Interactive visualization will not work.")
        print_warning("Visualizations will still be saved to files.")
    
    return has_gui

def run_test_visualization():
    """Run a test visualization to ensure everything works."""
    print_header("Testing Visualization")
    
    try:
        print_step("Importing visualization module...")
        # Add the project directory to the path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        
        import visualization
        print_success("Visualization module imported successfully")
        
        if hasattr(visualization, 'HAS_MATPLOTLIB') and visualization.HAS_MATPLOTLIB:
            print_success("Matplotlib is available")
        else:
            print_warning("Matplotlib is not available")
        
        if hasattr(visualization, 'HAS_NETWORKX') and visualization.HAS_NETWORKX:
            print_success("NetworkX is available")
        else:
            print_warning("NetworkX is not available")
            
        if hasattr(visualization, 'HAS_PIL') and visualization.HAS_PIL:
            print_success("PIL is available")
        else:
            print_warning("PIL is not available")
        
        if hasattr(visualization, 'has_interactive_backend') and visualization.has_interactive_backend:
            print_success("Interactive backend is available")
        else:
            print_warning("Interactive backend is not available")
        
        return True
    
    except ImportError as e:
        print_error(f"Failed to import visualization module: {e}")
        return False
    
    except Exception as e:
        print_error(f"Error during visualization test: {e}")
        return False

def check_version_compatibility():
    """Check Python version compatibility."""
    print_header("Checking Python Version")
    
    py_version = sys.version_info
    print_step(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 6):
        print_error("Python 3.6 or higher is required")
        return False
    
    print_success("Python version is compatible")
    return True

def main():
    """Main installer function."""
    print(f"""{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║  Wireless Network Simulator - Dependency Installer        ║
║  Platform: {platform.system()} {platform.release()}              ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
""")
    
    # Check Python version
    if not check_version_compatibility():
        sys.exit(1)
    
    # Check system dependencies
    check_system_dependencies()
    
    # Install core dependencies
    if not install_core_dependencies():
        print_warning("Some core dependencies could not be installed")
        print_warning("The simulator may not work correctly")
    
    # Install GUI dependencies
    install_gui_dependencies()
    
    # Test visualization
    run_test_visualization()
    
    print(f"""{Colors.GREEN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║  Installation Complete                                    ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
""")
    
    print("To run the simulator with interactive visualization:")
    print(f"    {sys.executable} simulation.py --interactive")
    print("\nTo run the simulator with automatic dependency installation:")
    print(f"    {sys.executable} simulation.py --auto-install")
    print("\nTo run the simulator with both options:")
    print(f"    {sys.executable} simulation.py --interactive --auto-install")

if __name__ == "__main__":
    main()
