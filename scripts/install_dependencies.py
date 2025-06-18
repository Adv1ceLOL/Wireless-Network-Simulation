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
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Disable colors if running on Windows cmd or if redirected to a file
if platform.system() == 'Windows' and not os.environ.get('WT_SESSION') and not os.environ.get('TERM_PROGRAM'):
    # Windows Command Prompt doesn't support ANSI colors by default
    for attr in dir(Colors):
        if not attr.startswith('__'):
            setattr(Colors, attr, '')

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}== {text} =={Colors.END}\n")

def print_status(package, status, details=""):
    """Print the status of a package check."""
    if status == "OK":
        status_color = Colors.GREEN
        status_text = "OK"
    elif status == "MISSING":
        status_color = Colors.RED
        status_text = "MISSING"
    elif status == "OUTDATED":
        status_color = Colors.YELLOW
        status_text = "OUTDATED"
    elif status == "INSTALLING":
        status_color = Colors.BLUE
        status_text = "INSTALLING"
    elif status == "ERROR":
        status_color = Colors.RED
        status_text = "ERROR"
    else:
        status_color = ""
        status_text = status
    
    package_name = f"{package:<15}"
    status_formatted = f"{status_color}{status_text}{Colors.END}"
    
    if details:
        print(f"  {package_name} [{status_formatted}] - {details}")
    else:
        print(f"  {package_name} [{status_formatted}]")

def check_package(package, min_version=None):
    """Check if a package is installed and meets minimum version."""
    spec = importlib.util.find_spec(package)
    
    if spec is None:
        return False, None, "Not installed"
    
    # Try to get the version
    try:
        module = importlib.import_module(package)
        version = getattr(module, '__version__', None)
        
        if version is None and hasattr(module, 'version'):
            version = module.version
            
        if version is None and package == 'matplotlib':
            version = module.__version__
            
        if version is None and package == 'networkx':
            version = module.__version__
            
        if version is None and package == 'PIL':
            version = module.PILLOW_VERSION if hasattr(module, 'PILLOW_VERSION') else module.__version__
            
        if min_version is not None and version is not None:
            from pkg_resources import parse_version
            if parse_version(version) < parse_version(min_version):
                return False, version, f"Version {version} < {min_version}"
                
        return True, version, f"Version {version}"
    except Exception as e:
        return True, None, f"Installed, but couldn't determine version: {str(e)}"

def install_package(package, version=None, upgrade=False):
    """Install a Python package using pip."""
    try:
        pip_cmd = [sys.executable, '-m', 'pip', 'install']
        
        if upgrade:
            pip_cmd.append('--upgrade')
            
        if version:
            pip_cmd.append(f'{package}=={version}')
        else:
            pip_cmd.append(package)
            
        print_status(package, "INSTALLING")
        process = subprocess.run(pip_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if process.returncode != 0:
            print_status(package, "ERROR", process.stderr.strip())
            return False
            
        return True
    except Exception as e:
        print_status(package, "ERROR", str(e))
        return False

def main():
    """Main function to check and install dependencies."""
    print_header("Wireless Network Simulator - Dependency Checker")
    
    # Create necessary directories
    print("Creating necessary directories...")
    os.makedirs(os.path.join("output", "visualizations"), exist_ok=True)
    os.makedirs(os.path.join("output", "reports"), exist_ok=True)
    
    # Check Python version
    print_header("Checking Python Version")
    python_version = platform.python_version()
    min_python = "3.6"
    
    if python_version < min_python:
        print_status("Python", "OUTDATED", f"Found {python_version}, need {min_python}+")
        print(f"{Colors.RED}Error: Python {min_python}+ is required.{Colors.END}")
        sys.exit(1)
    else:
        print_status("Python", "OK", f"Found {python_version}")
    
    # Required packages
    print_header("Checking Required Packages")
    required_packages = {
        "matplotlib": "3.0.0",
        "networkx": "2.0",
        "PIL": "7.0.0"  # Pillow
    }
    
    missing_packages = []
    outdated_packages = []
    
    for package, min_version in required_packages.items():
        installed, version, details = check_package(package, min_version)
        
        if not installed and package == "PIL":
            # Try with Pillow instead
            installed, version, details = check_package("PIL.Image")
            if installed:
                details = "PIL is available through Pillow"
                
        if not installed and version is None:
            print_status(package, "MISSING", details)
            missing_packages.append(package)
        elif not installed:
            print_status(package, "OUTDATED", details)
            outdated_packages.append(package)
        else:
            print_status(package, "OK", details)
    
    # Install missing packages
    if missing_packages or outdated_packages or args.force:
        print_header("Installing Missing/Outdated Packages")
        
        # Install pip if needed
        try:
            import pip
        except ImportError:
            print_status("pip", "MISSING")
            print(f"{Colors.YELLOW}Attempting to install pip...{Colors.END}")
            try:
                subprocess.check_call([sys.executable, '-m', 'ensurepip'])
                print_status("pip", "OK", "Installed successfully")
            except:
                print_status("pip", "ERROR", "Could not install pip")
                print(f"{Colors.RED}Error: pip is required to install dependencies.{Colors.END}")
                print(f"{Colors.RED}Please install pip manually and run this script again.{Colors.END}")
                sys.exit(1)
        
        # Install/upgrade packages
        for package in missing_packages:
            version = None
            if package == "PIL":
                package = "Pillow"  # Install Pillow instead of PIL
            install_package(package, version, False)
        
        for package in outdated_packages:
            version = None
            if package == "PIL":
                package = "Pillow"  # Upgrade Pillow instead of PIL
            install_package(package, version, True)
        
        if args.force:
            print(f"{Colors.BLUE}Reinstalling packages due to --force flag{Colors.END}")
            for package in required_packages:
                if package not in missing_packages and package not in outdated_packages:
                    if package == "PIL":
                        package = "Pillow"
                    install_package(package, None, True)
    
    # Check for GUI/interactive backend support
    if not args.no_interactive:
        print_header("Checking GUI Backend Support")
        try:
            import matplotlib
            backend = matplotlib.get_backend()
            print_status("matplotlib backend", "OK", f"Using {backend}")
            
            # Check if we can create a figure
            try:
                import matplotlib.pyplot as plt
                fig = plt.figure()
                plt.close(fig)
                print_status("matplotlib figure", "OK", "Can create figures")
            except Exception as e:
                print_status("matplotlib figure", "ERROR", str(e))
                print(f"{Colors.YELLOW}Warning: Might have issues with interactive visualization.{Colors.END}")
                
        except Exception as e:
            print_status("matplotlib backend", "ERROR", str(e))
    
    # Final check
    print_header("Final Check")
    all_packages_ok = True
    
    for package in required_packages:
        installed, version, details = check_package(package)
        if not installed and package == "PIL":
            # Try with Pillow instead
            installed, version, details = check_package("PIL.Image")
            
        if not installed:
            print_status(package, "MISSING", details)
            all_packages_ok = False
        else:
            print_status(package, "OK", details)
    
    if all_packages_ok:
        print(f"\n{Colors.GREEN}All dependencies are installed!{Colors.END}")
        return True
    else:
        print(f"\n{Colors.RED}Some dependencies are still missing.{Colors.END}")
        print(f"{Colors.RED}Please fix the issues above and run this script again.{Colors.END}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
