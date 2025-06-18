from network import SensorNetwork
from report_network import generate_network_report
import random
import sys
import os
import platform

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
    network.run_distance_vector_protocol()
    
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
    report_file = "network_report.txt"
    generate_network_report(network, output_file=report_file)
      # Handle visualization
    if interactive:
        try:
            # Check if auto_install is enabled
            if auto_install:
                print("\nChecking and installing visualization dependencies...")
                # Import the install function and run it
                try:
                    from visualization import check_and_install_dependencies
                    check_and_install_dependencies(auto_install=True)
                except ImportError:
                    print("Could not find dependency installer. Continuing with available packages.")
            
            from visualization import visualize_network
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
                from visualization import visualize_network
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
            from visualization import visualize_network
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
        print("Visualization files are saved in the visualizations directory.")
    else:
        print("Interactive visualizations should be displayed in separate windows.")
        print("Press Enter to close the visualization windows and exit...")
        
    print("Network report is saved in network_report.txt")
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