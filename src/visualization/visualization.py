import sys
import os
import platform
import importlib.util
import warnings
import subprocess
import shutil
import logging

# Import our backend handler
from src.visualization.visualization_backend import (
    initialize_backend, 
    is_package_installed, 
    fix_tkinter_windows,
    get_available_backends
)

# Import PIL visualization for fallback
from src.visualization.pil_visualization import visualize_network_pil

# Define module-level flags for dependency availability
HAS_MATPLOTLIB = is_package_installed('matplotlib')
HAS_NETWORKX = is_package_installed('networkx')
HAS_PIL = is_package_installed('PIL')

# Initialize matplotlib backend if available
if HAS_MATPLOTLIB:
    import matplotlib
    # Let the backend handler manage backend selection
    BACKEND_NAME, IS_INTERACTIVE = initialize_backend()
else:
    BACKEND_NAME, IS_INTERACTIVE = None, False

# Add a module-level variable to keep track of created figures
interactive_figures = []

# Function to install a package using pip
def install_package(package_name):
    """Install a Python package using pip."""
    try:
        print(f"Attempting to install {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}")
        return False

# Function to check and install required dependencies
def check_and_install_dependencies(auto_install=False):
    """Check if required visualization dependencies are installed and optionally install them."""
    dependencies = {
        'matplotlib': 'matplotlib',
        'networkx': 'networkx',
        'numpy': 'numpy'
    }
    
    # GUI backends
    gui_dependencies = {}
    if platform.system() == 'Windows':
        gui_dependencies['tkinter'] = 'tk'
        gui_dependencies['PyQt5'] = 'PyQt5'
    elif platform.system() == 'Darwin':  # macOS
        gui_dependencies['PyQt5'] = 'PyQt5'
        gui_dependencies['tkinter'] = 'tk'
    else:  # Linux
        gui_dependencies['PyQt5'] = 'PyQt5'
        # Note: tk for Linux usually requires system package manager
    
    missing_deps = {}
    missing_gui_deps = {}
    
    # Check core dependencies
    for dep_name, pip_name in dependencies.items():
        if not is_package_installed(dep_name):
            missing_deps[dep_name] = pip_name
    
    # Check GUI dependencies
    has_gui_backend = False
    for dep_name, pip_name in gui_dependencies.items():
        if is_package_installed(dep_name):
            has_gui_backend = True
        else:
            missing_gui_deps[dep_name] = pip_name
    
    # Install missing dependencies if auto_install is True
    if auto_install:
        for dep_name, pip_name in missing_deps.items():
            install_package(pip_name)
        
        # Only try to install GUI dependencies if no GUI backend is available
        if not has_gui_backend:
            for dep_name, pip_name in missing_gui_deps.items():
                success = install_package(pip_name)
                if success:
                    break  # Stop after installing one GUI backend
    
    # Return information about missing dependencies
    return {
        'core_dependencies': missing_deps,
        'gui_dependencies': missing_gui_deps,
        'has_gui_backend': has_gui_backend or len(missing_gui_deps) == 0
    }

# Check for interactive mode flag and auto-install flag
interactive_mode = '--interactive' in sys.argv or '-i' in sys.argv
auto_install = '--auto-install' in sys.argv

# Check dependencies and optionally install them
dependency_status = check_and_install_dependencies(auto_install)

has_interactive_backend = False

# Try to set the interactive backend if requested
if interactive_mode:
    if not dependency_status['has_gui_backend'] and not auto_install:
        print("\nInteractive mode was requested but no GUI backend is available.")
        print("Install one of the following packages to enable interactive mode:")
        for dep_name, pip_name in dependency_status['gui_dependencies'].items():
            print(f"  - {dep_name} (pip install {pip_name})")
        print("\nYou can also run with --auto-install to attempt automatic installation of dependencies.")
        print("Continuing in non-interactive mode. Visualizations will be saved to files.")
    else:
        try:
            available_backends = get_available_backends()
            has_interactive_backend = len(available_backends) > 0 and available_backends[0] != 'Agg'
        except Exception as e:
            print(f"Error setting up interactive backend: {e}")
            print("Continuing with non-interactive mode")
            matplotlib.use('Agg', force=True)
else:
    # Ensure we're using Agg for non-interactive mode
    matplotlib.use('Agg', force=True)

# Now it's safe to import the required visualization libraries
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.cm as cm
    
    # Enable interactive mode if we have an interactive backend
    if has_interactive_backend and interactive_mode:
        plt.ion()  # Turn on interactive mode
        print("Matplotlib interactive mode enabled")
    
    HAS_MATPLOTLIB = True
except ImportError as e:
    print(f"Error importing matplotlib: {e}")
    print("Matplotlib visualizations will not be available")
    HAS_MATPLOTLIB = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError as e:
    print(f"Error importing networkx: {e}")
    print("NetworkX visualizations will not be available")
    HAS_NETWORKX = False

def visualize_network(network, interactive=False, clear_previous=False, title=None):
    """Visualize the sensor network using multiple methods.
    
    Args:
        network: The sensor network to visualize
        interactive: Whether to display the plots interactively
        clear_previous: Whether to clear previous matplotlib figures
        title: Optional title for the visualizations
    """
    # Clear any previously tracked figures
    global interactive_figures
    interactive_figures = []
    
    # Clear previous figures if requested
    if clear_previous and HAS_MATPLOTLIB:
        import matplotlib.pyplot as plt
        plt.close('all')
    
    # Check if interactive flag is set through command line
    if '--interactive' in sys.argv or '-i' in sys.argv:
        interactive = True
    
    # Check if interactive mode is actually available
    if interactive and not has_interactive_backend:
        print("\nWARNING: Interactive mode requested but no interactive backend is available.")
        print("Visualizations will be saved to files instead of displayed.")
        interactive = False
    
    # Keep track of successful visualizations
    successful_viz = 0
    
    # Create a directory for visualizations if it doesn't exist
    viz_dir = "output/visualizations"
    try:
        if not os.path.exists(viz_dir):
            os.makedirs(viz_dir)
            print(f"Created visualization directory: {viz_dir}")
        viz_path = lambda f: os.path.join(viz_dir, f)
    except Exception:
        # Fall back to current directory if we can't create the visualization directory
        viz_path = lambda f: f
    
    # Try different visualization methods based on available dependencies
    successful_methods = []
    
    # Set up visualization paths
    if not interactive:
        # Ensure output directory exists
        output_dir = os.path.join("output", "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        
        # Set output paths
        matplotlib_file = os.path.join(output_dir, "network_visualization_matplotlib.png")
        networkx_file = os.path.join(output_dir, "network_visualization_networkx.png")
        adjacency_file = os.path.join(output_dir, "network_adjacency_list.png")
    else:
        matplotlib_file = networkx_file = adjacency_file = None
    
    # Try matplotlib visualization
    try:
        if visualize_network_matplotlib(network, matplotlib_file, interactive, title):
            successful_methods.append("matplotlib")
    except Exception as e:
        print(f"Error in matplotlib visualization: {e}")
    
    # Try networkx visualization
    try:
        if visualize_network_networkx(network, networkx_file, interactive, title):
            successful_methods.append("networkx")
    except Exception as e:
        print(f"Error in networkx visualization: {e}")
    
    # Try adjacency list visualization
    try:
        if visualize_adjacency_list(network, adjacency_file, interactive, title):
            successful_methods.append("adjacency_list")
    except Exception as e:
        print(f"Error in adjacency list visualization: {e}")
    
    # Fallback to PIL for non-interactive mode if needed
    if not interactive and not successful_methods and HAS_PIL:
        try:
            visualize_network_pil(network, os.path.join(output_dir, "network_visualization_simple.png"))
            successful_methods.append("pil")
        except Exception as e:
            print(f"Error in PIL visualization: {e}")
    
    if not interactive:
        if successful_methods:
            print(f"Successfully generated {len(successful_methods)} visualizations.")
            print(f"Visualization files were saved to the '{output_dir}' directory.")
        else:
            print("No visualizations could be generated. Please check dependencies.")
    else:
        if successful_methods:
            print(f"Visualizations are displayed in interactive windows.")
        else:
            print("No visualizations could be displayed. Please check dependencies.")
    
    return successful_methods

def print_adjacency_list(network):
    """Print the adjacency list representation of the network to the console."""
    print("\nADJACENCY LIST REPRESENTATION:")
    print("-----------------------------")
    
    # Sort nodes by ID
    sorted_nodes = sorted(network.nodes, key=lambda x: x.node_id)
    
    for node in sorted_nodes:
        # Get connected neighbors sorted by ID
        neighbors = sorted(node.connections.items(), key=lambda x: x[0])
        neighbor_str = ", ".join([f"{n_id} (delay: {delay:.2f})" for n_id, delay in neighbors])
        print(f"[{node.node_id}]: {neighbor_str}")

def visualize_network_matplotlib(network, output_file=None, interactive=False, title=None):
    """Visualize the sensor network using Matplotlib."""
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping matplotlib visualization")
        return False
    
    try:
        import matplotlib.pyplot as plt
        
        # Create figure
        plt.figure(figsize=(10, 8))
        
        # Add nodes to plot
        for node in network.nodes:
            plt.plot(node.x, node.y, 'o', markersize=10, label=f"Node {node.node_id}")
            plt.text(node.x, node.y, str(node.node_id), fontsize=12)
            
            # Draw transmission range circle
            circle = plt.Circle((node.x, node.y), node.transmission_range, 
                              fill=False, linestyle='--', alpha=0.3)
            plt.gca().add_patch(circle)
            
            # Draw connections
            for neighbor_id, delay in node.connections.items():
                neighbor = network.get_node_by_id(neighbor_id)
                if neighbor:
                    # Only draw connections in one direction (to avoid duplicates)
                    if node.node_id < neighbor_id:
                        plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 'b-', alpha=0.6)
                        # Add delay as a label near the middle of the line
                        mid_x = (node.x + neighbor.x) / 2
                        mid_y = (node.y + neighbor.y) / 2
                        plt.text(mid_x, mid_y, f"{delay:.2f}", fontsize=8, 
                                backgroundcolor='white', alpha=0.8)
        
        # Set plot limits with some padding
        padding = max([node.transmission_range for node in network.nodes] + [1])
        plt.xlim(-padding, max([node.x for node in network.nodes]) + padding)
        plt.ylim(-padding, max([node.y for node in network.nodes]) + padding)
        
        # Set plot title
        if title:
            plt.title(title)
        else:
            plt.title(f"Wireless Sensor Network ({len(network.nodes)} nodes)")
            
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.grid(True, alpha=0.3)
        
        # Handle output
        if interactive:
            # Track the figure for later closing
            interactive_figures.append(plt.gcf())
            plt.show(block=False)
            print("Displayed interactive matplotlib visualization")
        elif output_file:
            plt.savefig(output_file, dpi=150)
            print(f"Saved network visualization to {output_file}")
            plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error in matplotlib visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

def visualize_network_networkx(network, output_file=None, interactive=False, title=None):
    """Visualize the sensor network using NetworkX."""
    if not HAS_NETWORKX or not HAS_MATPLOTLIB:
        print("NetworkX or Matplotlib not available, skipping networkx visualization")
        return False
    
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
        
        # Create a new graph
        G = nx.Graph()
        
        # Add nodes with positions
        for node in network.nodes:
            G.add_node(node.node_id, pos=(node.x, node.y), 
                     range=node.transmission_range)
        
        # Add edges with weights
        for node in network.nodes:
            for neighbor_id, delay in node.connections.items():
                G.add_edge(node.node_id, neighbor_id, weight=delay)
        
        # Get positions for drawing
        pos = nx.get_node_attributes(G, 'pos')
        
        # Create figure
        plt.figure(figsize=(10, 8))
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
        
        # Draw edges with weights as labels
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        edge_labels = {k: f"{v:.2f}" for k, v in edge_labels.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
        
        # Set plot title
        if title:
            plt.title(title)
        else:
            plt.title(f"Network Graph ({len(network.nodes)} nodes, {G.number_of_edges()} connections)")
        
        plt.axis('off')
        
        # Handle output
        if interactive:
            # Track the figure for later closing
            interactive_figures.append(plt.gcf())
            plt.show(block=False)
            print("Displayed interactive NetworkX visualization")
        elif output_file:
            plt.savefig(output_file, dpi=150)
            print(f"Saved network visualization to {output_file}")
            plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error in networkx visualization: {e}")
        return False

def visualize_adjacency_list(network, output_file=None, interactive=False, title=None):
    """Visualize the network as an adjacency list."""
    if interactive and not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping interactive adjacency list visualization")
        return False
    
    try:
        # Sort nodes by ID for consistent output
        sorted_nodes = sorted(network.nodes, key=lambda node: node.node_id)
        
        adjacency_list = []
        adjacency_list.append("ADJACENCY LIST REPRESENTATION:")
        adjacency_list.append("-----------------------------")
        
        for node in sorted_nodes:
            # Get connected neighbors sorted by ID
            neighbors = sorted(node.connections.items(), key=lambda x: x[0])
            neighbor_str = ", ".join([f"{n_id} (delay: {delay:.2f})" for n_id, delay in neighbors])
            adjacency_list.append(f"[{node.node_id}]: {neighbor_str}")
        
        # Join with newlines for display
        adjacency_text = "\n".join(adjacency_list)
        
        # Print to console
        print(adjacency_text)
        
        # Handle output depending on mode
        if interactive:
            import matplotlib.pyplot as plt
            from matplotlib.font_manager import FontProperties
            
            # Create a figure with text
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Turn off axes
            ax.axis('off')
            
            # Set figure title
            if title:
                ax.set_title(title)
            else:
                ax.set_title(f"Network Adjacency List ({len(network.nodes)} nodes)")
            
            # Display the text
            font_prop = FontProperties(family='monospace')
            ax.text(0.05, 0.95, adjacency_text, transform=ax.transAxes,
                  fontproperties=font_prop, verticalalignment='top')
            
            # Track the figure for later closing
            interactive_figures.append(plt.gcf())
            plt.show(block=False)
            print("Displayed interactive adjacency list visualization")
            
        elif output_file:
            # Create image from text
            try:
                # Use PIL to create an image
                from PIL import Image, ImageDraw, ImageFont
                import numpy as np
                
                # Estimate image size based on text content
                line_count = len(adjacency_list)
                max_line_length = max(len(line) for line in adjacency_list)
                
                # Create image
                font_size = 14
                char_width = font_size * 0.6
                line_height = font_size * 1.5
                
                img_width = int(max_line_length * char_width + 40)
                img_height = int(line_count * line_height + 40)
                
                # Create a white image
                img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                
                # Try to load a monospace font
                try:
                    if platform.system() == "Windows":
                        font = ImageFont.truetype("consolas", font_size)
                    elif platform.system() == "Darwin":  # macOS
                        font = ImageFont.truetype("Menlo", font_size)
                    else:  # Linux and others
                        font = ImageFont.truetype("DejaVuSansMono", font_size)
                except Exception:
                    # Fallback to default font
                    font = ImageFont.load_default()
                
                # Add title
                title_text = title if title else f"Network Adjacency List ({len(network.nodes)} nodes)"
                draw.text((20, 10), title_text, fill=(0, 0, 0), font=font)
                
                # Draw the text
                y = 10 + line_height
                for line in adjacency_list:
                    draw.text((20, y), line, fill=(0, 0, 0), font=font)
                    y += line_height
                
                # Save the image
                img.save(output_file)
                print(f"Saved adjacency list to {output_file}")
                
            except Exception as e:
                print(f"Error creating adjacency list image: {e}")
                # Fallback to saving as text file
                text_file = output_file.replace('.png', '.txt')
                with open(text_file, 'w') as f:
                    f.write(adjacency_text)
                print(f"Saved adjacency list as text to {text_file}")
        
        return True
        
    except Exception as e:
        print(f"Error in adjacency list visualization: {e}")
        return False
