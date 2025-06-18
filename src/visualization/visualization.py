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

def visualize_network(network, interactive=False):
    """Visualize the sensor network using multiple methods.
    
    Args:
        network: The sensor network to visualize
        interactive: Whether to display the plots interactively
    """
    # Clear any previously tracked figures
    global interactive_figures
    interactive_figures = []
    
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
    
    if HAS_MATPLOTLIB:
        try:
            # Create matplotlib visualization
            visualize_network_matplotlib(network, 
                                       output_file=viz_path("network_visualization_matplotlib.png"), 
                                       interactive=interactive)
            successful_viz += 1
        except Exception as e:
            print(f"Error in matplotlib visualization: {e}")
    else:
        print("Matplotlib visualization skipped (library not available)")
    
    if HAS_MATPLOTLIB and HAS_NETWORKX:
        try:
            # Create networkx visualization
            visualize_network_networkx(network, 
                                     output_file=viz_path("network_visualization_networkx.png"), 
                                     interactive=interactive)
            successful_viz += 1
        except Exception as e:
            print(f"Error in networkx visualization: {e}")
    else:
        print("NetworkX visualization skipped (library not available)")
    
    if HAS_MATPLOTLIB:
        try:
            # Create adjacency list visualization
            visualize_adjacency_list(network, 
                                   output_file=viz_path("network_adjacency_list.png"), 
                                   interactive=interactive)
            successful_viz += 1
        except Exception as e:
            print(f"Error in adjacency list visualization: {e}")
    
    # Try alternative simple visualization if matplotlib fails
    if successful_viz == 0 and HAS_PIL:
        try:
            visualize_network_pil(network, output_file=viz_path("network_visualization_simple.png"))
            successful_viz += 1
        except Exception as e:
            print(f"Error in PIL visualization: {e}")
    
    # Always try to print the adjacency list to console even if visualization fails
    try:
        print_adjacency_list(network)
    except Exception as e:
        print(f"Error printing adjacency list: {e}")
    
    if successful_viz == 0:
        print("\nWARNING: No visualizations could be generated!")
        print("Please check your matplotlib and networkx installations.")
        print("You can still view the network details in the console output and report file.")
    else:
        print(f"\nSuccessfully generated {successful_viz} visualizations.")
        if not interactive:
            print(f"Visualization files were saved to the '{viz_dir}' directory.")
        else:
            print(f"Visualizations are displayed in interactive windows.")

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

def visualize_network_matplotlib(network, output_file="network_visualization_matplotlib.png", interactive=False):
    """Visualize the sensor network using Matplotlib."""
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping matplotlib visualization")
        return
        
    try:
        plt.figure(figsize=(12, 10))
        
        # Find max coordinates for setting plot limits
        max_x = max(node.x for node in network.nodes) * 1.1
        max_y = max(node.y for node in network.nodes) * 1.1
        
        # Plot nodes
        for node in network.nodes:
            plt.scatter(node.x, node.y, s=120, color='blue', edgecolor='black', zorder=10)
            plt.text(node.x + 0.1, node.y + 0.1, f"{node.node_id}", 
                    fontweight='bold', fontsize=12, zorder=15)
            
            # Draw transmission range circle
            circle = plt.Circle((node.x, node.y), node.transmission_range, 
                               alpha=0.1, color='blue', zorder=5)
            plt.gca().add_patch(circle)
            
            # Draw connections with color indicating delay
            for neighbor_id, delay in node.connections.items():
                neighbor = network.get_node_by_id(neighbor_id)
                # Only draw connection if this node has lower ID (to avoid duplicates)
                if node.node_id < neighbor_id:
                    # Use color to represent delay (red=high delay, green=low delay)
                    color = plt.cm.RdYlGn_r(delay)
                    plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 
                            alpha=0.7,
                            linewidth=1.5,
                            color=color,
                            zorder=1)
                    # Add delay label to midpoint of connection
                    mid_x = (node.x + neighbor.x) / 2
                    mid_y = (node.y + neighbor.y) / 2
                    plt.text(mid_x, mid_y, f"{delay:.2f}", fontsize=8, 
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                            zorder=8,
                            ha='center', va='center')
        
        plt.xlim(0, max_x)
        plt.ylim(0, max_y)
        plt.title("Wireless Sensor Network Simulation (Matplotlib)")
        plt.xlabel("X position")
        plt.ylabel("Y position")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add a colorbar for delay reference
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca())
        cbar.set_label('Delay Value', rotation=270, labelpad=15)
        cbar.ax.set_yticklabels(['Low', '', 'Medium', '', 'High'])
        
        plt.tight_layout()
        
        # In interactive mode, just show the plot without saving
        if interactive and has_interactive_backend:
            try:
                plt.draw()  # Draw the current figure
                plt.pause(0.001)  # Add a small pause to allow the window to appear without blocking
                print("Displayed interactive matplotlib visualization")
                # Keep a reference to the figure to prevent it from being garbage collected
                global interactive_figures
                interactive_figures.append(plt.gcf())
                return
            except Exception as e:
                print(f"Failed to show interactive plot: {e}")
                # Fall back to saving if interactive display fails
        
        # If not interactive mode or if interactive display failed, save to file
        try:
            plt.savefig(output_file, dpi=300)
            print(f"Saved network visualization to {output_file}")
        except Exception as e:
            print(f"Failed to save visualization to file: {e}")
        
        plt.close()  # Close the figure to free memory
    
    except Exception as e:
        print(f"Error in matplotlib visualization: {e}")
        # Try to close any open figures to prevent resource leaks
        try:
            plt.close()
        except:
            pass
        raise  # Re-raise the exception to be handled by the caller

def visualize_network_networkx(network, output_file="network_visualization_networkx.png", interactive=False):
    """Visualize the sensor network using NetworkX."""
    if not HAS_NETWORKX or not HAS_MATPLOTLIB:
        print("NetworkX or Matplotlib not available, skipping networkx visualization")
        return
        
    try:
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes with positions
        node_positions = {}
        for node in network.nodes:
            G.add_node(node.node_id)
            node_positions[node.node_id] = (node.x, node.y)
        
        # Add edges with delay weights
        edge_weights = {}
        for node in network.nodes:
            for neighbor_id, delay in node.connections.items():
                if node.node_id < neighbor_id:  # Avoid duplicates
                    G.add_edge(node.node_id, neighbor_id, weight=delay)
                    edge_weights[(node.node_id, neighbor_id)] = delay
        
        plt.figure(figsize=(12, 10))
        
        # Draw nodes with labels
        nx.draw_networkx_nodes(G, node_positions, node_size=700, 
                             node_color='lightblue', edgecolors='navy', alpha=0.8)
        nx.draw_networkx_labels(G, node_positions, font_weight='bold', font_size=10)
        
        # Draw edges with colors based on weights
        edges = list(G.edges())
        if not edges:
            print("Warning: Network has no edges, graph will be empty")
            
        weights = [edge_weights.get((u, v)) or edge_weights.get((v, u), 0.5) for u, v in edges]
        
        # Create colormap: green for low delays, red for high delays
        cmap = LinearSegmentedColormap.from_list('delay_cmap', ['green', 'yellow', 'red'])
        
        # Normalize weights for colormap
        if weights:
            norm = plt.Normalize(min(weights), max(weights))
            edge_colors = [cmap(norm(weight)) for weight in weights]
            
            # Draw edges with variable width based on weight (inverse: thicker = lower delay)
            edge_widths = [3 * (1 - w) + 0.5 for w in weights]  # Thicker lines for lower delays
            
            nx.draw_networkx_edges(G, node_positions, edgelist=edges, 
                                  width=edge_widths, edge_color=edge_colors, alpha=0.7)
            
            # Add edge labels (delay values)
            edge_labels = {(u, v): f"{w:.2f}" for (u, v), w in zip(edges, weights)}
            nx.draw_networkx_edge_labels(G, node_positions, edge_labels=edge_labels, 
                                       font_size=8, bbox=dict(facecolor='white', alpha=0.7))
        
        plt.title("Wireless Sensor Network Visualization (NetworkX)")
        plt.axis('off')  # Hide axes
        
        # Add colorbar for delay reference
        if weights:
            sm = cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=plt.gca(), label='Delay')
            cbar.ax.set_yticklabels(['Low', '', 'Medium', '', 'High'])
        
        plt.tight_layout()
        
        # In interactive mode, just show the plot without saving
        if interactive and has_interactive_backend:
            try:
                plt.draw()  # Draw the current figure
                plt.pause(0.001)  # Add a small pause to allow the window to appear without blocking
                print("Displayed interactive NetworkX visualization")
                # Keep a reference to the figure to prevent it from being garbage collected
                global interactive_figures
                interactive_figures.append(plt.gcf())
                return
            except Exception as e:
                print(f"Failed to show interactive plot: {e}")
                # Fall back to saving if interactive display fails
        
        # If not interactive mode or if interactive display failed, save to file
        try:
            plt.savefig(output_file, dpi=300)
            print(f"Saved network visualization to {output_file}")
        except Exception as e:
            print(f"Failed to save visualization to file: {e}")
        
        plt.close()  # Close the figure to free memory
            
    except Exception as e:
        print(f"Error in networkx visualization: {e}")
        # Try to close any open figures to prevent resource leaks
        try:
            plt.close()
        except:
            pass
        raise  # Re-raise the exception to be handled by the caller

def visualize_adjacency_list(network, output_file="network_adjacency_list.png", interactive=False):
    """Generate and display adjacency list representation of the network."""
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping adjacency list visualization")
        return
        
    try:
        plt.figure(figsize=(10, 8))
        plt.axis('off')  # Turn off axis
        
        # Create adjacency list text
        adj_list = ["Adjacency List Representation:"]
        adj_list.append("")
        
        # Sort nodes by ID
        sorted_nodes = sorted(network.nodes, key=lambda x: x.node_id)
        
        for node in sorted_nodes:
            # Get connected neighbors sorted by ID
            neighbors = sorted(node.connections.items(), key=lambda x: x[0])
            neighbor_str = ", ".join([f"{n_id} (delay: {delay:.2f})" for n_id, delay in neighbors])
            adj_list.append(f"[{node.node_id}]: {neighbor_str}")
        
        # Join with newlines
        adj_text = "\n".join(adj_list)
        
        # Create a text box with a border
        plt.text(0.05, 0.95, adj_text, fontsize=12, family='monospace',
                 verticalalignment='top', horizontalalignment='left',
                 transform=plt.gca().transAxes,
                 bbox=dict(facecolor='#f9f9f9', edgecolor='gray', boxstyle='round,pad=1.0', alpha=0.95))
        
        plt.title("Network Adjacency List")
        plt.tight_layout()
        
        # In interactive mode, just show the plot without saving
        if interactive and has_interactive_backend:
            try:
                plt.draw()  # Draw the current figure
                plt.pause(0.001)  # Add a small pause to allow the window to appear without blocking
                print("Displayed interactive adjacency list visualization")
                # Keep a reference to the figure to prevent it from being garbage collected
                global interactive_figures
                interactive_figures.append(plt.gcf())
                return
            except Exception as e:
                print(f"Failed to show interactive plot: {e}")
                # Fall back to saving if interactive display fails
        
        # If not interactive mode or if interactive display failed, save to file
        try:
            plt.savefig(output_file, dpi=300)
            print(f"Saved adjacency list to {output_file}")
        except Exception as e:
            print(f"Failed to save adjacency list to file: {e}")
        
        plt.close()  # Close the figure to free memory
            
    except Exception as e:
        print(f"Error in adjacency list visualization: {e}")
        # Try to close any open figures to prevent resource leaks
        try:
            plt.close()
        except:
            pass
        raise  # Re-raise the exception to be handled by the caller
