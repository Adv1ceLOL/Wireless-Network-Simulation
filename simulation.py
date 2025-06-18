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

def run_dynamic_scenario(network, time_steps=20, p_request=0.3, p_fail=0.1, p_new=0.1, 
                        interactive=False, delay_between_steps=1.0, verbose=True):
    """Run a dynamic scenario simulation with probabilistic events.
    
    Args:
        network: The initialized SensorNetwork to run the simulation on
        time_steps: Number of time steps to simulate
        p_request: Probability of a packet send request arriving at each time step
        p_fail: Probability of a random link disappearing at each time step
        p_new: Probability of a new link appearing at each time step
        interactive: Whether to show visualizations during simulation
        delay_between_steps: Delay between time steps (seconds)
        verbose: Whether to print detailed information
        
    Returns:
        Dictionary with simulation statistics
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"DYNAMIC SCENARIO SIMULATION")
        print(f"Time steps: {time_steps}, P(request): {p_request}, P(fail): {p_fail}, P(new): {p_new}")
        print(f"{'='*70}\n")
    
    # Statistics tracking
    stats = {
        "requests": 0,
        "successful_transmissions": 0,
        "failed_transmissions": 0,
        "links_removed": 0,
        "links_added": 0,
        "total_delay": 0,
        "reconvergence_iterations": 0,
        "events_by_step": []
    }
    
    n_nodes = len(network.nodes)
    
    # Run the protocol initially to ensure routing tables are built
    initial_iterations = network.run_distance_vector_protocol(verbose=verbose)
    if verbose:
        print(f"Initial protocol convergence: {initial_iterations} iterations")
    
    # Simulate time steps
    for t in range(time_steps):
        step_events = {"step": t+1, "events": []}
        
        if verbose:
            print(f"\n--- Time Step {t+1}/{time_steps} ---")
            print("[Step] Exchanging hello messages...")
        # 1. Hello message exchange (simulate)
        # ...existing code...
        # 1. Randomly remove links with probability p_fail
        if random.random() < p_fail and len(network.get_all_links()) > 0:
            # Select a random existing link
            links = network.get_all_links()
            if links:
                node_a_id, node_b_id, _ = random.choice(links)
                if verbose:
                    print(f"[Step] Link failure: Connection between Node {node_a_id} and Node {node_b_id} disappeared")
                # Remove the link
                iterations = network.handle_topology_change(node_a_id, node_b_id, new_delay=None, verbose=verbose)
                stats["links_removed"] += 1
                stats["reconvergence_iterations"] += iterations
                step_events["events"].append(f"Link removed: {node_a_id}-{node_b_id}")
                if verbose:
                    print(f"[Step] Protocol reconverged after {iterations} iterations")
        # 2. Randomly add new links with probability p_new
        if random.random() < p_new:
            # Find nodes that aren't connected
            unconnected_pairs = []
            for i in range(n_nodes):
                for j in range(i+1, n_nodes):
                    if j not in network.nodes[i].connections:
                        # Check if they're within range
                        node_a = network.nodes[i]
                        node_b = network.nodes[j]
                        if node_a.can_reach(node_b) or node_b.can_reach(node_a):
                            unconnected_pairs.append((i, j))
            if unconnected_pairs:
                node_a_id, node_b_id = random.choice(unconnected_pairs)
                delay = random.uniform(0.1, 1.0)
                if verbose:
                    print(f"[Step] New link: Connection established between Node {node_a_id} and Node {node_b_id} with delay {delay:.4f}")
                # Add the link
                iterations = network.handle_topology_change(node_a_id, node_b_id, new_delay=delay, verbose=verbose)
                stats["links_added"] += 1
                stats["reconvergence_iterations"] += iterations
                step_events["events"].append(f"Link added: {node_a_id}-{node_b_id}")
                if verbose:
                    print(f"[Step] Protocol reconverged after {iterations} iterations")
        # 3. Process random packet requests with probability p_request
        if random.random() < p_request:
            source_id = random.randint(0, n_nodes-1)
            dest_id = random.randint(0, n_nodes-1)
            while dest_id == source_id:
                dest_id = random.randint(0, n_nodes-1)
            message = f"Packet at t={t+1}"
            if verbose:
                print(f"[Step] Packet request: Node {source_id} → Node {dest_id}")
            path, delay = network.simulate_message_transmission(source_id, dest_id, message, verbose=verbose)
            stats["requests"] += 1
            if path:
                stats["successful_transmissions"] += 1
                stats["total_delay"] += delay
                step_events["events"].append(f"Transmission: {source_id}→{dest_id} succeeded")
            else:
                stats["failed_transmissions"] += 1
                step_events["events"].append(f"Transmission: {source_id}→{dest_id} failed")
        if verbose:
            print("[Step] Routing tables updated.")
        
        # Visualize the network state if in interactive mode
        if interactive:
            try:
                from src.visualization.visualization import visualize_network
                visualize_network(network, interactive=True, clear_previous=True, 
                                 title=f"Network State at Step {t+1}/{time_steps}")
                
                # Give time to view the visualization
                print(f"Network state at step {t+1}/{time_steps}. Press Enter to continue...")
                input()
            except Exception as e:
                print(f"Visualization error: {e}")
        
        stats["events_by_step"].append(step_events)
        
        # Add delay between steps
        if t < time_steps - 1 and delay_between_steps > 0:
            time.sleep(delay_between_steps)
    
    # Print simulation summary
    if verbose:
        print(f"\n{'='*70}")
        print("DYNAMIC SCENARIO SIMULATION SUMMARY")
        print(f"{'='*70}")
        print(f"Time steps: {time_steps}")
        print(f"Packet requests: {stats['requests']}")
        print(f"Successful transmissions: {stats['successful_transmissions']} ({stats['successful_transmissions']/stats['requests']*100:.1f}% success rate)" if stats['requests'] > 0 else "Successful transmissions: 0 (0% success rate)")
        print(f"Average delay for successful transmissions: {stats['total_delay']/stats['successful_transmissions']:.4f}" if stats['successful_transmissions'] > 0 else "Average delay: N/A")
        print(f"Links removed: {stats['links_removed']}")
        print(f"Links added: {stats['links_added']}")
        print(f"Total protocol reconvergence iterations: {stats['reconvergence_iterations']}")
        print(f"Average iterations per topology change: {stats['reconvergence_iterations']/(stats['links_removed']+stats['links_added']):.2f}" if (stats['links_removed']+stats['links_added']) > 0 else "Average iterations per change: N/A")
    
    return stats

def run_simulation(n_nodes=10, area_size=10, transmission_tests=3, interactive=False, auto_install=False, 
                  dynamic_scenario=False, time_steps=20, p_request=0.3, p_fail=0.1, p_new=0.1, delay_between_steps=1.0):
    """Run a wireless sensor network simulation.
    
    Args:
        n_nodes: Number of nodes in the network
        area_size: Size of the simulation area
        transmission_tests: Number of random transmissions to test
        interactive: Whether to display interactive visualizations
        auto_install: Whether to automatically install missing dependencies
        dynamic_scenario: Whether to run a dynamic scenario simulation
        time_steps: Number of time steps for dynamic scenario
        p_request: Probability of a packet request in dynamic scenario
        p_fail: Probability of a link failure in dynamic scenario
        p_new: Probability of a new link in dynamic scenario
        delay_between_steps: Delay between time steps in dynamic scenario
    """
    print(f"\n{'='*70}")
    print(f"WIRELESS SENSOR NETWORK SIMULATION")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"{'='*70}\n")
    
    print(f"Creating a wireless sensor network with {n_nodes} nodes")
    
    # Create and set up network
    network = SensorNetwork()
    network.create_random_network(n_nodes, area_size)
    
    # If running dynamic scenario, hand off to that function
    if dynamic_scenario:
        return run_dynamic_scenario(network, time_steps=time_steps, 
                                   p_request=p_request, p_fail=p_fail, p_new=p_new,
                                   interactive=interactive, delay_between_steps=delay_between_steps)
    
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
    dynamic_scenario = "--dynamic" in sys.argv
    
    # Get number of nodes from command line if specified
    n_nodes = 15
    time_steps = 20
    p_request = 0.3
    p_fail = 0.1
    p_new = 0.1
    delay_between_steps = 1.0
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--nodes='):
                try:
                    n_nodes = int(arg.split('=')[1])
                except ValueError:
                    print(f"Warning: Invalid node count format. Using default ({n_nodes}).")
            elif arg.startswith('--time-steps='):
                try:
                    time_steps = int(arg.split('=')[1])
                except ValueError:
                    print(f"Warning: Invalid time steps format. Using default ({time_steps}).")
            elif arg.startswith('--p-request='):
                try:
                    p_request = float(arg.split('=')[1])
                    if not 0 <= p_request <= 1:
                        print(f"Warning: p_request must be between 0 and 1. Using default ({p_request}).")
                        p_request = 0.3
                except ValueError:
                    print(f"Warning: Invalid p_request format. Using default ({p_request}).")
            elif arg.startswith('--p-fail='):
                try:
                    p_fail = float(arg.split('=')[1])
                    if not 0 <= p_fail <= 1:
                        print(f"Warning: p_fail must be between 0 and 1. Using default ({p_fail}).")
                        p_fail = 0.1
                except ValueError:
                    print(f"Warning: Invalid p_fail format. Using default ({p_fail}).")
            elif arg.startswith('--p-new='):
                try:
                    p_new = float(arg.split('=')[1])
                    if not 0 <= p_new <= 1:
                        print(f"Warning: p_new must be between 0 and 1. Using default ({p_new}).")
                        p_new = 0.1
                except ValueError:
                    print(f"Warning: Invalid p_new format. Using default ({p_new}).")
            elif arg.startswith('--delay='):
                try:
                    delay_between_steps = float(arg.split('=')[1])
                except ValueError:
                    print(f"Warning: Invalid delay format. Using default ({delay_between_steps}).")
    
    # Run the simulation
    network = run_simulation(n_nodes=n_nodes, transmission_tests=5, 
                           interactive=interactive_mode, auto_install=auto_install,
                           dynamic_scenario=dynamic_scenario, time_steps=time_steps,
                           p_request=p_request, p_fail=p_fail, p_new=p_new,
                           delay_between_steps=delay_between_steps)
    
    # Generate visualizations in non-interactive mode if not already done
    if not dynamic_scenario and not interactive_mode:
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
    print("  --dynamic                 : Run dynamic scenario simulation")
    print("  --time-steps=<number>     : Number of time steps for dynamic scenario (default: 20)")
    print("  --p-request=<float>       : Probability of packet request (default: 0.3)")
    print("  --p-fail=<float>          : Probability of link failure (default: 0.1)")
    print("  --p-new=<float>           : Probability of new link (default: 0.1)")
    print("  --delay=<float>           : Delay between time steps in seconds (default: 1.0)")
    
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