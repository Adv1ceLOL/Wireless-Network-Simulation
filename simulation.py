from src.core.network import SensorNetwork
from src.reporting.report_network import generate_network_report
from src.visualization.visualization import (
    visualize_network_matplotlib,
    visualize_network_networkx,
    visualize_adjacency_list
)
import random
import sys
import os
import platform
import time

def run_simulation(n_nodes=10, area_size=10, transmission_tests=3, interactive=False, auto_install=False):
    """Run a wireless sensor network simulation.
    
    Args:
        n_nodes: Number of nodes in the network
        area_size: Size of the simulation area
        transmission_tests: Number of random transmissions to test
        interactive: Whether to display interactive visualizations
        auto_install: Whether to automatically install missing dependencies
    """
    print(f"\n{'='*70}")
    print(f"WIRELESS SENSOR NETWORK SIMULATION")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"{'='*70}\n")
    
    print(f"Creating a wireless sensor network with {n_nodes} nodes")
    
    # Create and set up network
    network = SensorNetwork()
    network.create_random_network(n_nodes, area_size)
    
    print("Running proactive distance vector protocol for network discovery...")
    iterations = network.run_distance_vector_protocol(verbose=True)
    print(f"Protocol converged after {iterations} iterations")
    
    # Print network information
    print(f"\nNetwork created with {len(network.nodes)} nodes:")
    for node in network.nodes:
        print(f"  {node}")
        neighbors = [f"Node {n_id} (delay: {delay:.3f})" for n_id, delay in node.connections.items()]
        if neighbors:
            print(f"    Connected to: {', '.join(neighbors)}")
    
    # Run some random transmissions
    print(f"\n{'-' * 50}")
    print("Running transmission simulations...")
    
    successful_transmissions = 0
    total_delay = 0
    
    for i in range(transmission_tests):
        source_id = random.randint(0, n_nodes-1)
        target_id = random.randint(0, n_nodes-1)
        while target_id == source_id:
            target_id = random.randint(0, n_nodes-1)
            
        message = f"Test message {i+1}"
        path, delay = network.simulate_message_transmission(source_id, target_id, message)
        
        if path:
            successful_transmissions += 1
            total_delay += delay
    
    # Demonstrate proactive network changes
    if n_nodes >= 3:
        print(f"\n{'-' * 50}")
        print("Demonstrating proactive distance vector protocol with network changes...")
        
        # Choose two random nodes with a connection
        connected_pairs = []
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if j in network.nodes[i].connections:
                    connected_pairs.append((i, j))
        
        if connected_pairs:
            # Remove a random connection
            node_a, node_b = random.choice(connected_pairs)
            print(f"\nRemoving connection between Node {node_a} and Node {node_b}")
            
            # Store routing info before change for comparison
            path_before, delay_before = network._find_shortest_path(node_a, node_b)
            if path_before:
                print(f"Before change - Path from {node_a} to {node_b}: {' -> '.join(map(str, path_before))}")
                print(f"Before change - Delay: {delay_before:.4f}")
            
            # Apply the topology change
            print("\nApplying topology change and running distance vector protocol...")
            reconverge_iterations = network.handle_topology_change(node_a, node_b, new_delay=None, verbose=False)
            print(f"Protocol reconverged after {reconverge_iterations} iterations")
            
            # Check the new routing
            path_after, delay_after = network._find_shortest_path(node_a, node_b)
            if path_after:
                print(f"After change - Path from {node_a} to {node_b}: {' -> '.join(map(str, path_after))}")
                print(f"After change - Delay: {delay_after:.4f}")
            else:
                print(f"After change - No path available from {node_a} to {node_b}")
            
            # Run a test transmission with changed topology
            network.simulate_message_transmission(node_a, node_b, "Test after topology change")
            
            # Add a new connection with different delay
            print(f"\nAdding new connection between Node {node_a} and Node {node_b} with different delay")
            new_delay = random.uniform(0.1, 2.0)
            print(f"New delay: {new_delay:.4f}")
            reconverge_iterations = network.handle_topology_change(node_a, node_b, new_delay=new_delay, verbose=False)
            print(f"Protocol reconverged after {reconverge_iterations} iterations")
            
            # Check the final routing
            path_final, delay_final = network._find_shortest_path(node_a, node_b)
            if path_final:
                print(f"Final path from {node_a} to {node_b}: {' -> '.join(map(str, path_final))}")
                print(f"Final delay: {delay_final:.4f}")
                
            # Run a test transmission with restored topology
            network.simulate_message_transmission(node_a, node_b, "Test after restoring connection")
    
    # Print summary
    print(f"\n{'-' * 50}")
    print("Simulation Summary:")
    print(f"  Transmission attempts: {transmission_tests}")
    print(f"  Successful transmissions: {successful_transmissions}")
    if successful_transmissions > 0:
        print(f"  Average delay: {total_delay/successful_transmissions:.4f} units")
    print(f"  Success rate: {successful_transmissions/transmission_tests:.1%}")
    
    # Generate detailed network report
    print("\nGenerating detailed network report...")
    report_dir = os.path.join("output", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, "network_report.txt")
    generate_network_report(network, output_file=report_file)
    
    # Handle visualization
    if interactive:
        try:
            # Check if auto_install is enabled
            if auto_install:
                print("\nChecking and installing visualization dependencies...")
                # Import the install function and run it
                try:
                    from src.visualization.visualization import check_and_install_dependencies
                    check_and_install_dependencies(auto_install=True)
                except ImportError:
                    print("Could not find dependency installer. Continuing with available packages.")
            
            from src.visualization.visualization import visualize_network
            print("\nGenerating interactive network visualizations...")
            visualize_network(network, interactive=True)
        except ImportError as e:
            print(f"\nInteractive visualization module not available: {e}")
            print("Continuing without interactive visualizations.")
            
            if auto_install:
                print("Automatic installation was attempted but failed.")
                print("Please check your internet connection or try manual installation:")
            else:
                print("To enable visualizations, you can:")
                print("  1. Run with --auto-install: python simulation.py --interactive --auto-install")
                print("  2. Run the installer: python install_dependencies.py")
                print("  3. Manually install the packages:")
            
            print("    pip install matplotlib networkx pillow")
            
            if platform.system() == "Windows":
                print("    Make sure you have tkinter installed (comes with standard Python installation)")
            elif platform.system() == "Linux":
                print("    sudo apt-get install python3-tk  # For Debian/Ubuntu")
            elif platform.system() == "Darwin":  # macOS
                print("    pip install PyQt5  # Alternative GUI backend for macOS")
        except Exception as e:
            print(f"\nError in interactive visualization: {e}")
            print("Falling back to non-interactive visualizations.")
            try:
                from src.visualization.visualization import visualize_network
                visualize_network(network, interactive=False)
            except Exception as e2:
                print(f"Visualization failed: {e2}")
    
    return network

if __name__ == "__main__":
    # Check for command line arguments
    interactive_mode = "--interactive" in sys.argv or "-i" in sys.argv
    auto_install = "--auto-install" in sys.argv
    
    # Get number of nodes from command line if specified
    n_nodes = 15
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--nodes='):
                try:
                    n_nodes = int(arg.split('=')[1])
                except ValueError:
                    print(f"Warning: Invalid node count format. Using default ({n_nodes}).")    
    # Run the simulation
    network = run_simulation(n_nodes=n_nodes, transmission_tests=5, 
                             interactive=interactive_mode, auto_install=auto_install)
    
    # Generate visualizations in non-interactive mode if not already done
    if not interactive_mode:
        try:
            from src.visualization.visualization import visualize_network
            print("\nGenerating network visualizations...")
            visualize_network(network, interactive=False)
        except ImportError as e:
            print(f"\nVisualization module not available: {e}")
            print("Make sure you have all required packages installed (matplotlib, networkx)")
            print("Install them with: pip install matplotlib networkx")
            print("Or run with: python simulation.py --auto-install to automatically install dependencies")
        except Exception as e:
            print(f"\nError in visualization: {e}")
            print("Visualization failed, but simulation completed successfully.")
    print("\nSimulation complete!")
    if not interactive_mode:
        print("Visualization files are saved in the output/visualizations directory.")
    else:
        print("Interactive visualizations should be displayed in separate windows.")
        print("Press Enter to close the visualization windows and exit...")
        
    print("Network report is saved in the output/reports directory.")
    
    # Provide help for PowerShell users who might have issues with && operator
    if platform.system() == "Windows":
        print("\nTIP: If you're using PowerShell and want to run with specific parameters:")
        print("  python simulation.py --nodes=20; python simulation.py --interactive")
        print("  # Use semicolon instead of && for command chaining in PowerShell")
    
    # Show available command-line options
    print("\nAvailable command-line options:")
    print("  --interactive, -i         : Enable interactive visualizations")
    print("  --auto-install            : Automatically install missing dependencies")
    print("  --nodes=<number>          : Set the number of nodes in the network")
    
    # If in interactive mode, wait for user input to keep the windows open
    if interactive_mode:
        try:
            input("\nPress Enter to close all visualization windows and exit...")
        except KeyboardInterrupt:
            pass
        finally:
            # Try to close all open matplotlib figures
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except:
                pass