#!/usr/bin/env python3
"""
Wireless Network Simulator - Visualization Backend Handler
---------------------------------------------------------
This module manages different visualization backends and provides
fallback mechanisms when primary backends fail.
"""

import sys
import os
import platform
import importlib.util
import subprocess
import logging
import warnings
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('visualization_backend')

# Suppress matplotlib warnings about font cache
warnings.filterwarnings("ignore", ".*Matplotlib is building the font cache using fc-list.*")
warnings.filterwarnings("ignore", category=UserWarning)

# Define backend priorities by platform
BACKEND_PRIORITIES = {
    'Windows': ['TkAgg', 'Qt5Agg', 'Qt4Agg', 'wxAgg', 'Agg'],
    'Darwin': ['MacOSX', 'TkAgg', 'Qt5Agg', 'Qt4Agg', 'wxAgg', 'Agg'],  # macOS
    'Linux': ['TkAgg', 'GTK3Agg', 'Qt5Agg', 'Qt4Agg', 'wxAgg', 'Agg']
}

# Backend to GUI package mapping
GUI_PACKAGES = {
    'TkAgg': 'tkinter',
    'Qt5Agg': 'PyQt5',
    'Qt4Agg': 'PyQt4',
    'wxAgg': 'wx',
    'GTK3Agg': 'gi',
    'MacOSX': None  # Built-in on macOS
}

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

def fix_tkinter_windows():
    """Apply workarounds for Tcl/Tk initialization issues on Windows."""
    if platform.system() != 'Windows':
        return
    
    # Attempt to fix Tcl/Tk initialization error on Windows
    if is_package_installed('tkinter'):
        try:
            # Set environment variable to work around threading issues
            os.environ['TCL_LIBRARY'] = os.path.join(sys.base_prefix, 'tcl', 'tcl8.6')
            os.environ['TK_LIBRARY'] = os.path.join(sys.base_prefix, 'tcl', 'tk8.6')
            
            # Pre-initialize tkinter to prevent later issues
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            # Keep a reference to prevent garbage collection
            sys._tkinter_root = root
            
            logger.info("Successfully initialized tkinter on Windows")
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize tkinter on Windows: {e}")
            return False
    return False

@contextmanager
def suppress_exceptions():
    """Context manager to suppress exceptions and log them."""
    try:
        yield
    except Exception as e:
        logger.warning(f"Suppressed exception: {e}")

def get_available_backends():
    """Get a list of available GUI backends for the current platform."""
    system = platform.system()
    if system not in BACKEND_PRIORITIES:
        system = 'Linux'  # Default to Linux priorities
    
    available = []
    for backend in BACKEND_PRIORITIES[system]:
        required_package = GUI_PACKAGES.get(backend)
        
        # Skip backend if it requires a package that's not installed
        if required_package and not is_package_installed(required_package):
            continue
            
        # Special handling for MacOSX backend on Darwin
        if backend == 'MacOSX' and system != 'Darwin':
            continue
            
        available.append(backend)
    
    return available

def initialize_backend(force_agg=False):
    """
    Initialize the best available matplotlib backend.
    
    Args:
        force_agg: Force using the non-interactive 'Agg' backend
        
    Returns:
        tuple: (backend_name, is_interactive)
    """
    # Always import matplotlib here to avoid early backend selection
    import matplotlib
    
    # If we're forcing Agg, just use it
    if force_agg:
        matplotlib.use('Agg', force=True)
        return 'Agg', False
    
    # On Windows, try to fix tkinter issues
    if platform.system() == 'Windows':
        fix_tkinter_windows()
    
    # Try available backends in priority order
    backends = get_available_backends()
    
    for backend in backends:
        try:
            logger.info(f"Trying {backend} backend...")
            matplotlib.use(backend, force=True)
            
            # Test if the backend works by importing it
            backend_module = f"matplotlib.backends.backend_{backend.lower()}"
            with suppress_exceptions():
                __import__(backend_module)
                
                # For TkAgg, we need special testing on Windows
                if backend == 'TkAgg' and platform.system() == 'Windows':
                    import matplotlib.pyplot as plt
                    # Try creating a figure with the backend
                    fig = plt.figure(figsize=(1, 1))
                    plt.close(fig)
                
                logger.info(f"Successfully initialized {backend} backend")
                return backend, backend != 'Agg'
                
        except Exception as e:
            logger.warning(f"Backend {backend} failed: {e}")
    
    # If all else fails, use Agg
    logger.warning("All interactive backends failed, falling back to Agg")
    matplotlib.use('Agg', force=True)
    return 'Agg', False

def get_image_library():
    """Get the best available image manipulation library."""
    if is_package_installed('PIL'):
        from PIL import Image, ImageDraw
        return Image, ImageDraw
    return None, None

def test_backend():
    """Test if the visualization backend works correctly."""
    backend, is_interactive = initialize_backend()
    
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title("Backend Test")
        
        if is_interactive:
            plt.close(fig)
            return True, backend
        else:
            plt.savefig("backend_test.png")
            plt.close(fig)
            return False, backend
            
    except Exception as e:
        logger.error(f"Backend test failed: {e}")
        return False, None

if __name__ == "__main__":
    # Run a backend test if this module is executed directly
    success, backend = test_backend()
    if success:
        print(f"Backend test successful using {backend}")
    else:
        print(f"Backend test failed or non-interactive backend {backend} was used")
