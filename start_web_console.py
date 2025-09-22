#!/usr/bin/env python3
"""
Startup script for the Wireless Sensor Network Web Console
This script will install dependencies and launch the web interface.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_dependencies():
    """Check if required packages are available."""
    required_packages = ['flask', 'flask_socketio']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def main():
    print("🌐 Wireless Sensor Network Simulator - Web Console")
    print("=" * 50)
    
    # Check if we're in the correct directory
    if not os.path.exists('simulation.py') or not os.path.exists('src'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing packages: {missing}")
        print("Installing missing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)
    
    # Import and run the web console
    try:
        print("🚀 Starting web console...")
        print("📱 Access the interface at: http://localhost:5001")
        print("🔧 Use Ctrl+C to stop the server")
        print("-" * 50)
        
        # Import here after dependencies are confirmed
        from web_console import app, socketio
        socketio.run(app, host='0.0.0.0', port=5001, debug=False)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Web console stopped by user")
    except Exception as e:
        print(f"❌ Error starting web console: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
