from typing import Dict, List, Tuple, Union, Optional, Any
from src.core.network import SensorNetwork  # type: ignore
from src.reporting.report_network import generate_network_report  # type: ignore
from src.core.evaluation import run_evaluation  # type: ignore
import random
import os
import platform
import time
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger: logging.Logger = logging.getLogger('wireless_network_sim')

# Add these functions to count messages
def get_hello_msg_count(network: SensorNetwork) -> int:
    """Count all hello messages across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        # Adding a default of 0 if the attribute doesn't exist
        count += getattr(node, "hello_msg_count", 0)  # type: ignore
    return count


def get_topology_msg_count(network: SensorNetwork) -> int:
    """Count all topology discovery messages across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        # Adding a default of 0 if the attribute doesn't exist
        count += getattr(node, "topology_msg_count", 0)  # type: ignore
    return count


def get_route_discovery_msg_count(network: SensorNetwork) -> int:
    """Count all route discovery control packets across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        # Adding a default of 0 if the attribute doesn't exist
        count += getattr(node, "route_discovery_msg_count", 0)  # type: ignore
    return count


def get_data_packet_count(network: SensorNetwork) -> int:
    """Count all data packets forwarded across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        # Adding a default of 0 if the attribute doesn't exist
        count += getattr(node, "data_packet_count", 0)  # type: ignore
    return count


def get_total_message_count(network: SensorNetwork) -> int:
    """Get the total of all message types"""
    return (
        get_hello_msg_count(network)
        + get_topology_msg_count(network)
        + get_route_discovery_msg_count(network)
        + get_data_packet_count(network)
    )


def run_dynamic_scenario(
    network: SensorNetwork,
    time_steps: int = 20,
    p_request: float = 0.3,
    p_fail: float = 0.1,
    p_new: float = 0.1,
    interactive: bool = False,
    delay_between_steps: float = 1.0,
    verbose: bool = True,
) -> Dict[str, Any]:
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
        # Main simulation header is important info for the user
        print(f"\n{'='*70}")
        print("DYNAMIC SCENARIO SIMULATION")
        print(
            f"Time steps: {time_steps}, P(request): {p_request}, P(fail): {p_fail}, P(new): {p_new}"
        )
        print(f"{'='*70}\n")
        # Log the same information
        logger.info(f"Starting dynamic scenario simulation - Time steps: {time_steps}, P(request): {p_request}, P(fail): {p_fail}, P(new): {p_new}")

    # Statistics tracking
    stats: Dict[str, Any] = {
        "requests": 0,
        "successful_transmissions": 0,
        "failed_transmissions": 0,
        "links_removed": 0,
        "links_added": 0,
        "total_delay": 0,
        "reconvergence_iterations": 0,
        "events_by_step": [],
    }

    n_nodes: int = len(network.nodes)  # type: ignore

    # Run the protocol initially to ensure routing tables are built
    initial_iterations: int = network.run_distance_vector_protocol(verbose=verbose)  # type: ignore
    if verbose:
        logger.info(f"Initial protocol convergence: {initial_iterations} iterations")
    # Simulate time steps
    for t in range(time_steps):
        step_events: Dict[str, Any] = {"step": t + 1, "events": []}

        if verbose:
            print(f"\n--- Time Step {t+1}/{time_steps} ---")
            logger.debug("[Step] Exchanging hello messages...")

        # 1. Hello message exchange
        # Increment hello message counters for each node based on its connections
        for node in network.nodes:  # type: ignore
            # Each node sends one hello message to each of its neighbors
            hello_msgs: int = len(node.connections)  # type: ignore
            node.hello_msg_count += hello_msgs  # type: ignore

        # 2. Randomly remove links with probability p_fail
        if random.random() < p_fail and len(network.get_all_links()) > 0:  # type: ignore
            # Select a random existing link
            links: List[Tuple[int, int, float]] = network.get_all_links()  # type: ignore
            if links:
                node_a_id: int
                node_b_id: int
                _: float
                node_a_id, node_b_id, _ = random.choice(links)
                if verbose:
                    logger.warning(
                        f"[Step] Link failure: Connection between Node {node_a_id} and Node {node_b_id} disappeared"
                    )
                # Remove the link
                iterations: int = network.handle_topology_change(  # type: ignore
                    node_a_id, node_b_id, new_delay=None, verbose=verbose
                )
                stats["links_removed"] += 1
                stats["reconvergence_iterations"] += iterations
                step_events["events"].append(f"Link removed: {node_a_id}-{node_b_id}")
                if verbose:
                    logger.debug(f"[Step] Protocol reconverged after {iterations} iterations")
        # 2. Randomly add new links with probability p_new
        if random.random() < p_new:
            # Find nodes that aren't connected
            unconnected_pairs: List[Tuple[int, int]] = []
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    if j not in network.nodes[i].connections:  # type: ignore
                        # Check if they're mutually within range
                        node_a = network.nodes[i]  # type: ignore
                        node_b = network.nodes[j]  # type: ignore
                        if node_a.can_reach(node_b) and node_b.can_reach(node_a):  # type: ignore
                            unconnected_pairs.append((i, j))
            if unconnected_pairs:
                node_a_id: int
                node_b_id: int
                node_a_id, node_b_id = random.choice(unconnected_pairs)
                delay: float = random.uniform(0.1, 1.0)
                if verbose:
                    logger.info(
                        f"[Step] New link: Connection established between Node {node_a_id} and Node {node_b_id} with delay {delay:.4f}"
                    )
                # Add the link
                iterations: int = network.handle_topology_change(  # type: ignore
                    node_a_id, node_b_id, new_delay=delay, verbose=verbose
                )
                stats["links_added"] += 1
                stats["reconvergence_iterations"] += iterations
                step_events["events"].append(f"Link added: {node_a_id}-{node_b_id}")
                if verbose:
                    logger.debug(f"[Step] Protocol reconverged after {iterations} iterations")
        # 3. Process random packet requests with probability p_request
        if random.random() < p_request:
            source_id: int = random.randint(0, n_nodes - 1)
            dest_id: int = random.randint(0, n_nodes - 1)
            while dest_id == source_id:
                dest_id = random.randint(0, n_nodes - 1)
            message: str = f"Packet at t={t+1}"
            if verbose:
                logger.info(f"[Step] Packet request: Node {source_id} → Node {dest_id}")
            result = network.simulate_message_transmission(  # type: ignore
                source_id, dest_id, message, verbose=verbose
            )
            path: Optional[List[int]] = result[0]
            delay: float = result[1]
            stats["requests"] += 1
            if path:
                stats["successful_transmissions"] += 1
                stats["total_delay"] += delay
                step_events["events"].append(
                    f"Transmission: {source_id}→{dest_id} succeeded"
                )
            else:
                stats["failed_transmissions"] += 1
                step_events["events"].append(
                    f"Transmission: {source_id}→{dest_id} failed"
                )
        if verbose:
            logger.debug("[Step] Routing tables updated.")

        # Visualize the network state if in interactive mode
        if interactive:
            try:
                from src.visualization.visualization import visualize_network  # type: ignore

                visualize_network(  # type: ignore
                    network,
                    interactive=True,
                    clear_previous=True,
                    title=f"Network State at Step {t+1}/{time_steps}",
                )

                # Give time to view the visualization
                print(
                    f"Network state at step {t+1}/{time_steps}. Press Enter to continue..."
                )
                input()
            except Exception as e:
                logger.error(f"Visualization error: {e}")

        stats["events_by_step"].append(step_events)

        # Add delay between steps
        if t < time_steps - 1 and delay_between_steps > 0:
            time.sleep(delay_between_steps)

    # Print simulation summary
    if verbose:
        # Important summary headers remain as print statements for visibility
        print(f"\n{'='*70}")
        print("DYNAMIC SCENARIO SIMULATION SUMMARY")
        print(f"{'='*70}")
        print(f"Time steps: {time_steps}")
        print(f"Packet requests: {stats['requests']}")
        print(
            f"Successful transmissions: {stats['successful_transmissions']} ({stats['successful_transmissions']/stats['requests']*100:.1f}% success rate)"
            if stats["requests"] > 0
            else "Successful transmissions: 0 (0% success rate)"
        )
        print(
            f"Average delay for successful transmissions: {stats['total_delay']/stats['successful_transmissions']:.4f}"
            if stats["successful_transmissions"] > 0
            else "Average delay: N/A"
        )
        print(f"Links removed: {stats['links_removed']}")
        print(f"Links added: {stats['links_added']}")
        print(
            f"Total protocol reconvergence iterations: {stats['reconvergence_iterations']}"
        )
        print(
            f"Average iterations per topology change: {stats['reconvergence_iterations']/(stats['links_removed']+stats['links_added']):.2f}"
            if (stats["links_removed"] + stats["links_added"]) > 0
            else "Average iterations per change: N/A"
        )

        # Display message counters
        print("\nMessage Exchange Counters:")
        print(f"  Hello Messages: {get_hello_msg_count(network)}")
        print(f"  Topology Discovery Messages: {get_topology_msg_count(network)}")
        print(
            f"  Route Discovery Control Packets: {get_route_discovery_msg_count(network)}"
        )
        print(f"  Data Packets Forwarded: {get_data_packet_count(network)}")
        print(f"  Total Message Exchanges: {get_total_message_count(network)}")

    return stats


def run_simulation(
    n_nodes: int = 10,
    area_size: int = 10,
    transmission_tests: int = 3,
    interactive: bool = False,
    dynamic_scenario: bool = False,
    time_steps: int = 20,
    p_request: float = 0.3,
    p_fail: float = 0.1,
    p_new: float = 0.1,
    delay_between_steps: float = 1.0,
) -> Union[SensorNetwork, Dict[str, Any]]:
    """Run a wireless sensor network simulation.

    Args:
        n_nodes: Number of nodes in the network
        area_size: Size of the simulation area
        transmission_tests: Number of random transmissions to test
        interactive: Whether to display interactive visualizations
        dynamic_scenario: Whether to run a dynamic scenario simulation
        time_steps: Number of time steps for dynamic scenario
        p_request: Probability of a packet request in dynamic scenario
        p_fail: Probability of a link failure in dynamic scenario
        p_new: Probability of a new link in dynamic scenario
        delay_between_steps: Delay between time steps in dynamic scenario
    """
    # Main simulation header remains as print statement for user visibility
    print(f"\n{'='*70}")
    print("WIRELESS SENSOR NETWORK SIMULATION")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"{'='*70}\n")
    
    logger.info(f"Starting wireless sensor network simulation on {platform.system()} {platform.release()}")
    logger.info(f"Creating a wireless sensor network with {n_nodes} nodes")
    print(f"Creating a wireless sensor network with {n_nodes} nodes")

    # Create and set up network
    network: SensorNetwork = SensorNetwork()
    network.create_random_network(n_nodes, area_size)  # type: ignore

    # If running dynamic scenario, hand off to that function
    if dynamic_scenario:
        return run_dynamic_scenario(
            network,
            time_steps=time_steps,
            p_request=p_request,
            p_fail=p_fail,
            p_new=p_new,
            interactive=interactive,
            delay_between_steps=delay_between_steps,
        )

    print("Running proactive distance vector protocol for network discovery...")
    iterations: int = network.run_distance_vector_protocol(verbose=True)  # type: ignore
    print(f"Protocol converged after {iterations} iterations")

    # Print network information
    print(f"\nNetwork created with {len(network.nodes)} nodes:")  # type: ignore
    for node in network.nodes:  # type: ignore
        print(f"  {node}")
        neighbors: List[str] = [
            f"Node {n_id} (delay: {delay:.3f})"
            for n_id, delay in node.connections.items()  # type: ignore
        ]
        if neighbors:
            print(f"    Connected to: {', '.join(neighbors)}")

    # Run some random transmissions
    print(f"\n{'-' * 50}")
    print("Running transmission simulations...")
    logger.info(f"Running {transmission_tests} random transmission tests")

    successful_transmissions: int = 0
    total_delay: float = 0

    for i in range(transmission_tests):
        source_id: int = random.randint(0, n_nodes - 1)
        target_id: int = random.randint(0, n_nodes - 1)
        while target_id == source_id:
            target_id = random.randint(0, n_nodes - 1)

        message: str = f"Test message {i+1}"
        result = network.simulate_message_transmission(  # type: ignore
            source_id, target_id, message
        )
        path: Optional[List[int]] = result[0]
        delay: float = result[1]

        if path:
            successful_transmissions += 1
            total_delay += delay

    # Demonstrate proactive network changes
    if n_nodes >= 3:
        print(f"\n{'-' * 50}")
        print(
            "Demonstrating proactive distance vector protocol with network changes..."
        )

        # Choose two random nodes with a connection
        connected_pairs: List[Tuple[int, int]] = []
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if j in network.nodes[i].connections:  # type: ignore
                    connected_pairs.append((i, j))

        if connected_pairs:
            # Remove a random connection
            node_a: int
            node_b: int
            node_a, node_b = random.choice(connected_pairs)
            print(f"\nRemoving connection between Node {node_a} and Node {node_b}")

            # Store routing info before change for comparison
            # Note: Using protected method for demonstration - in production use public methods
            path_result_before = network._find_shortest_path(node_a, node_b)  # type: ignore
            path_before: Optional[List[int]] = path_result_before[0]
            delay_before: float = path_result_before[1]
            if path_before:
                print(
                    f"Before change - Path from {node_a} to {node_b}: {' -> '.join(map(str, path_before))}"
                )
                print(f"Before change - Delay: {delay_before:.4f}")

            # Apply the topology change
            print("\nApplying topology change and running distance vector protocol...")
            reconverge_iterations: int = network.handle_topology_change(  # type: ignore
                node_a, node_b, new_delay=None, verbose=False
            )
            print(f"Protocol reconverged after {reconverge_iterations} iterations")

            # Check the new routing
            path_result_after = network._find_shortest_path(node_a, node_b)  # type: ignore
            path_after: Optional[List[int]] = path_result_after[0]
            delay_after: float = path_result_after[1]
            if path_after:
                print(
                    f"After change - Path from {node_a} to {node_b}: {' -> '.join(map(str, path_after))}"
                )
                print(f"After change - Delay: {delay_after:.4f}")
            else:
                print(f"After change - No path available from {node_a} to {node_b}")

            # Run a test transmission with changed topology
            network.simulate_message_transmission(  # type: ignore
                node_a, node_b, "Test after topology change"
            )

            # Add a new connection with different delay
            print(
                f"\nAdding new connection between Node {node_a} and Node {node_b} with different delay"
            )
            new_delay: float = random.uniform(0.1, 2.0)
            print(f"New delay: {new_delay:.4f}")
            reconverge_iterations = network.handle_topology_change(  # type: ignore
                node_a, node_b, new_delay=new_delay, verbose=False
            )
            print(f"Protocol reconverged after {reconverge_iterations} iterations")

            # Check the final routing
            path_result_final = network._find_shortest_path(node_a, node_b)  # type: ignore
            path_final: Optional[List[int]] = path_result_final[0]
            delay_final: float = path_result_final[1]
            if path_final:
                print(
                    f"Final path from {node_a} to {node_b}: {' -> '.join(map(str, path_final))}"
                )
                print(f"Final delay: {delay_final:.4f}")

            # Run a test transmission with restored topology
            network.simulate_message_transmission(  # type: ignore
                node_a, node_b, "Test after restoring connection"
            )

    # Print summary
    print(f"\n{'-' * 50}")
    print("Simulation Summary:")
    print(f"  Transmission attempts: {transmission_tests}")
    print(f"  Successful transmissions: {successful_transmissions}")
    if successful_transmissions > 0:
        print(f"  Average delay: {total_delay/successful_transmissions:.4f} units")
    print(f"  Success rate: {successful_transmissions/transmission_tests:.1%}")

    # Print message counters
    print("\nMessage Exchange Counters:")
    print(f"  Hello Messages: {get_hello_msg_count(network)}")
    print(f"  Topology Discovery Messages: {get_topology_msg_count(network)}")
    print(
        f"  Route Discovery Control Packets: {get_route_discovery_msg_count(network)}"
    )
    print(f"  Data Packets Forwarded: {get_data_packet_count(network)}")
    print(f"  Total Message Exchanges: {get_total_message_count(network)}")

    # Generate detailed network report
    print("\nGenerating detailed network report...")
    report_dir = os.path.join("output", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, "network_report.txt")
    generate_network_report(network, output_file=report_file)  # type: ignore

    # Handle visualization
    if interactive:
        try:
            from src.visualization.visualization import visualize_network  # type: ignore

            print("\nGenerating interactive network visualizations...")
            logger.info("Generating interactive network visualizations")
            visualize_network(network, interactive=True)  # type: ignore
        except ImportError as e:
            print(f"\nInteractive visualization module not available: {e}")
            print("Continuing without interactive visualizations.")
            logger.warning(f"Interactive visualization module not available: {e}")

            print(
                "To enable visualizations, you can manually install the packages (pip install -r requirements.txt)"
            )

            if platform.system() == "Windows":
                print(
                    "    Make sure you have tkinter installed (comes with standard Python installation)"
                )
            elif platform.system() == "Linux":
                print("    sudo apt-get install python3-tk  # For Debian/Ubuntu")
            elif platform.system() == "Darwin":  # macOS
                print("    pip install PyQt5  # Alternative GUI backend for macOS")
        except Exception as e:
            print(f"\nError in interactive visualization: {e}")
            print("Falling back to non-interactive visualizations.")
            logger.error(f"Error in interactive visualization: {e}")
            logger.info("Falling back to non-interactive visualizations")
            try:
                from src.visualization.visualization import visualize_network  # type: ignore

                visualize_network(network, interactive=False)  # type: ignore
            except Exception as e2:
                print(f"Visualization failed: {e2}")
                logger.error(f"Visualization failed: {e2}")

    return network


if __name__ == "__main__":
    # Check for command line arguments

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Wireless Sensor Network Simulation")
    # Mode selection arguments
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enable interactive visualizations",
    )
    parser.add_argument(
        "--dynamic", action="store_true", help="Run dynamic scenario simulation"
    )
    parser.add_argument(
        "--evaluation", "-e", action="store_true", help="Run protocol evaluation mode"
    )

    # Basic simulation parameters
    parser.add_argument(
        "--nodes",
        type=int,
        default=15,
        help="Number of nodes in the network (default: 15)",
    )
    parser.add_argument(
        "--time-steps",
        type=int,
        default=20,
        help="Number of time steps for dynamic scenario (default: 20)",
    )

    # Probability parameters
    parser.add_argument(
        "--p-request",
        type=float,
        default=0.3,
        help="Probability of packet request in each time step (default: 0.3)",
    )
    parser.add_argument(
        "--p-fail",
        type=float,
        default=0.1,
        help="Probability of link failure in each time step (default: 0.1)",
    )
    parser.add_argument(
        "--p-new",
        type=float,
        default=0.1,
        help="Probability of new link in each time step (default: 0.1)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between time steps in seconds (default: 1.0)",
    )

    # Evaluation mode parameters
    parser.add_argument(
        "--topologies",
        type=int,
        default=5,
        help="Number of topologies to evaluate (default: 5)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Iterations per topology (default: 10)",
    )
    parser.add_argument(
        "--max-prob",
        type=float,
        default=0.3,
        help="Maximum probability for random parameters (default: 0.3)",
    )

    args: argparse.Namespace = parser.parse_args()

    # Extract arguments
    interactive_mode: bool = args.interactive
    dynamic_scenario: bool = args.dynamic
    evaluation_mode: bool = args.evaluation

    n_nodes: int = args.nodes
    time_steps: int = args.time_steps
    p_request: float = args.p_request
    p_fail: float = args.p_fail
    p_new: float = args.p_new
    delay_between_steps: float = args.delay

    # Evaluation mode parameters
    n_topologies: int = args.topologies
    iterations_per_topology: int = args.iterations
    max_probability: float = args.max_prob
    fixed_p_request: float = p_request  # Use the same p_request for evaluation mode

    # Validate probability values
    for name, value in [
        ("p_request", p_request),
        ("p_fail", p_fail),
        ("p_new", p_new),
        ("max_probability", max_probability),
    ]:
        if not 0 <= value <= 1:
            print(f"Warning: {name} must be between 0 and 1. Using default value.")
            logger.warning(f"Invalid {name} value: {value}, must be between 0 and 1. Using default value.")
            if name == "p_request":
                p_request = 0.3
                fixed_p_request = 0.3
            elif name == "p_fail":
                p_fail = 0.1
            elif name == "p_new":
                p_new = 0.1
            elif name == "max_probability":
                max_probability = 0.3

    # Run the simulation based on selected mode
    network: Optional[SensorNetwork] = None  # Ensure network is always defined (to avoid UnboundLocalError after)
    simulation_result: Union[SensorNetwork, Dict[str, Any], None] = None
    if evaluation_mode:
        # Run the evaluation mode
        results: Dict[str, Any] = run_evaluation(  # type: ignore
            n_topologies=n_topologies,
            iterations_per_topology=iterations_per_topology,
            max_probability=max_probability,
            n_nodes=n_nodes,
            area_size=10,
            fixed_p_request=fixed_p_request,
        )
    else:
        # Run the standard simulation
        simulation_result = run_simulation(
            n_nodes=n_nodes,
            transmission_tests=5,
            interactive=interactive_mode,
            dynamic_scenario=dynamic_scenario,
            time_steps=time_steps,
            p_request=p_request,
            p_fail=p_fail,
            p_new=p_new,
            delay_between_steps=delay_between_steps,
        )
        # If it's a dynamic scenario, simulation_result is a dict, otherwise it's a SensorNetwork
        if isinstance(simulation_result, SensorNetwork):
            network = simulation_result
    # Generate visualizations in non-interactive mode if not already done
    if not dynamic_scenario and not interactive_mode and network is not None:
        try:
            from src.visualization.visualization import visualize_network  # type: ignore

            print("\nGenerating network visualizations...")
            logger.info("Generating non-interactive network visualizations")
            visualize_network(network, interactive=False)  # type: ignore
        except ImportError as e:
            print(f"\nVisualization module not available: {e}")
            logger.error(f"Visualization module not available: {e}")
            print(
                "Make sure you have all required packages installed (matplotlib, networkx)"
            )
            print("Install them with: pip install matplotlib networkx")
            print(
                "Or run with: pip install -r requirements.txt to automatically install dependencies"
            )
        except Exception as e:
            print(f"\nError in visualization: {e}")
            print("Visualization failed, but simulation completed successfully.")
            logger.error(f"Error in visualization: {e}")
            logger.info("Simulation completed successfully despite visualization failure")

    print("\nSimulation complete!")
    logger.info("Simulation complete!")
    if not interactive_mode and not evaluation_mode:
        print("Visualization files are saved in the output/visualizations directory.")
    elif interactive_mode:
        print("Interactive visualizations should be displayed in separate windows.")
        print("Press Enter to close the visualization windows and exit...")

    if not evaluation_mode:
        print("Network report is saved in the output/reports directory.")
    else:
        print("Evaluation report is saved in the output/reports directory.")

    # Provide help for PowerShell users who might have issues with && operator
    if platform.system() == "Windows":
        print(
            "\nTIP: If you're using PowerShell and want to run with specific parameters:"
        )
        print("  python simulation.py --nodes=20; python simulation.py --interactive")
        print("  # Use semicolon instead of && for command chaining in PowerShell")
    # Show available command-line options
    print("\nAvailable command-line options:")
    print("  --interactive, -i         : Enable interactive visualizations")
    print("  --nodes=<number>          : Set the number of nodes in the network")
    print("  --dynamic                 : Run dynamic scenario simulation")
    print(
        "  --time-steps=<number>     : Number of time steps for dynamic scenario (default: 20)"
    )
    print("  --p-request=<float>       : Probability of packet request (default: 0.3)")
    print("  --p-fail=<float>          : Probability of link failure (default: 0.1)")
    print("  --p-new=<float>           : Probability of a new link (default: 0.1)")
    print(
        "  --delay=<float>           : Delay between time steps in seconds (default: 1.0)"
    )
    print("  --evaluation, -e          : Run protocol evaluation mode")
    print("  --topologies=<number>     : Number of topologies to evaluate (default: 5)")
    print("  --iterations=<number>     : Iterations per topology (default: 10)")
    print(
        "  --max-prob=<float>        : Maximum probability for random parameters p_fail and p_new (default: 0.3)"
    )

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

                plt.close("all")
            except Exception:
                pass
            
    # Final log message
    logger.info("Simulation program terminated")
