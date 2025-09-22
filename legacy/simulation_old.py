from typing import Dict, List, Tuple, Union, Optional, Any
from src.core.network import SensorNetwork  # type: ignore
from src.reporting.report_network import generate_network_report  # type: ignore
from src.core.evaluation import run_evaluation  # type: ignore
from src.core.deterministic_scenario import main as scenario_main  # type: ignore
import random
import os
import platform
import time
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger: logging.Logger = logging.getLogger('wireless_network_sim')

def get_hello_msg_count(network: SensorNetwork) -> int:
    """Count all hello messages across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        count += getattr(node, "hello_msg_count", 0)  # type: ignore
    return count


def get_topology_msg_count(network: SensorNetwork) -> int:
    """Count all topology discovery messages across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        count += getattr(node, "topology_msg_count", 0)  # type: ignore
    return count


def get_route_discovery_msg_count(network: SensorNetwork) -> int:
    """Count all route discovery control packets across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        count += getattr(node, "route_discovery_msg_count", 0)  # type: ignore
    return count


def get_data_packet_count(network: SensorNetwork) -> int:
    """Count all data packets forwarded across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
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
    hello_interval: int = 5,  # Send hello messages every N time steps
    ignore_initial_route_discovery: bool = True,
    seed: Optional[int] = None,
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
        hello_interval: Legacy parameter (hello messages now sent every step as per request.txt)
        ignore_initial_route_discovery: Whether to reset route discovery counters after initial convergence for static networks
        seed: Random seed for deterministic behavior (global random seed should be set before calling)

    Returns:
        Dictionary with simulation statistics
    """
    if verbose:
        print(f"\n{'='*70}")
        print("DYNAMIC SCENARIO SIMULATION")
        print(
            f"Time steps: {time_steps}, P(request): {p_request}, P(fail): {p_fail}, P(new): {p_new}"
        )
        print("Hello messages: Sent every time step (as per request.txt requirement)")
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
        "hello_exchanges": 0,
    }

    n_nodes: int = len(network.nodes)  # type: ignore

    initial_iterations: int = network.run_distance_vector_protocol(verbose=verbose)  # type: ignore
    if verbose:
        logger.info(f"Initial protocol convergence: {initial_iterations} iterations")
    
    if ignore_initial_route_discovery:
        if verbose:
            logger.debug("Resetting route discovery counters after initial convergence for efficiency analysis")
        for node in network.nodes:  # type: ignore
            node.route_discovery_msg_count = 0  # type: ignore
    
    significant_change: bool = False
    
    for t in range(time_steps):
        step_events: Dict[str, Any] = {"step": t + 1, "events": []}
        topology_changed: bool = False
        send_hello_this_step: bool = False

        if verbose:
            print(f"\n--- Time Step {t+1}/{time_steps} ---")

        send_hello_this_step = True
        if verbose:
            logger.debug("[Step] Sending hello messages (required every time step)...")
        
        if send_hello_this_step:
            hello_messages_sent = 0
            for node in network.nodes:  # type: ignore
                if len(node.connections) > 0:  # type: ignore
                    node.hello_msg_count += 1  # type: ignore
                    hello_messages_sent += 1
            stats["hello_exchanges"] += hello_messages_sent
            
            if verbose:
                logger.debug(f"[Step] {hello_messages_sent} hello broadcasts sent")

        if random.random() < p_fail and len(network.get_all_links()) > 0:  # type: ignore
            links: List[Tuple[int, int, float]] = network.get_all_links()  # type: ignore
            if links:
                node_a_id: int
                node_b_id: int
                _: float
                node_a_id, node_b_id, _ = random.choice(links)
                topology_changed = True
                if verbose:
                    logger.warning(
                        f"[Step] Link failure: Connection between Node {node_a_id} and Node {node_b_id} disappeared"
                    )
                iterations: int = network.handle_topology_change_optimized(  # type: ignore
                    node_a_id, node_b_id, new_delay=None, verbose=verbose
                )
                stats["links_removed"] += 1
                stats["reconvergence_iterations"] += iterations
                step_events["events"].append(f"Link removed: {node_a_id}-{node_b_id}")
                significant_change = (len(network.get_all_links()) < n_nodes)  # type: ignore
                if verbose:
                    logger.debug(f"[Step] Protocol reconverged after {iterations} iterations")
                    
        if random.random() < p_new:
            unconnected_pairs: List[Tuple[int, int]] = []
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    if j not in network.nodes[i].connections:  # type: ignore
                        node_a = network.nodes[i]  # type: ignore
                        node_b = network.nodes[j]  # type: ignore
                        if node_a.can_reach(node_b) and node_b.can_reach(node_a):  # type: ignore
                            unconnected_pairs.append((i, j))
            if unconnected_pairs:
                node_a_id: int
                node_b_id: int
                node_a_id, node_b_id = random.choice(unconnected_pairs)
                delay: float = random.uniform(0.1, 1.0)
                topology_changed = True
                if verbose:
                    logger.info(
                        f"[Step] New link: Connection established between Node {node_a_id} and Node {node_b_id} with delay {delay:.4f}"
                    )
                # Add the link with optimized reconvergence
                iterations: int = network.handle_topology_change_optimized(  # type: ignore
                    node_a_id, node_b_id, new_delay=delay, verbose=verbose
                )
                stats["links_added"] += 1
                stats["reconvergence_iterations"] += iterations
                step_events["events"].append(f"Link added: {node_a_id}-{node_b_id}")
                # New links are generally good, less disruptive than failures
                significant_change = False
                if verbose:
                    logger.debug(f"[Step] Protocol reconverged after {iterations} iterations")
                    
        # 4. Process random packet requests with probability p_request
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
            error_reason: Optional[str] = result[2] if len(result) > 2 else None
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
        if verbose and not topology_changed:
            logger.debug("[Step] Using cached routing tables - no topology changes")

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
        print(f"Hello message exchanges: {stats['hello_exchanges']}")
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

        # Calculate and display protocol efficiency table
        print(f"\n{'-' * 50}")
        print("PROTOCOL EFFICIENCY ANALYSIS")
        print(f"{'-' * 50}")
        
        hello_msgs = get_hello_msg_count(network)
        topology_msgs = get_topology_msg_count(network)
        route_discovery_msgs = get_route_discovery_msg_count(network)
        data_packets = get_data_packet_count(network)
        total_packets = get_total_message_count(network)
        
        # Calculate efficiency
        from src.core.evaluation import get_protocol_efficiency
        efficiency = get_protocol_efficiency(network)
        
        # Display efficiency table
        print(f"{'Metric':<25} | {'Count':<8} | {'Percentage':<10}")
        print(f"{'-'*25} | {'-'*8} | {'-'*10}")
        print(f"{'Hello Messages':<25} | {hello_msgs:<8} | {hello_msgs/total_packets*100:.2f}%" if total_packets > 0 else f"{'Hello Messages':<25} | {hello_msgs:<8} | {'0.00%':<10}")
        print(f"{'Topology Messages':<25} | {topology_msgs:<8} | {topology_msgs/total_packets*100:.2f}%" if total_packets > 0 else f"{'Topology Messages':<25} | {topology_msgs:<8} | {'0.00%':<10}")
        print(f"{'Route Discovery':<25} | {route_discovery_msgs:<8} | {route_discovery_msgs/total_packets*100:.2f}%" if total_packets > 0 else f"{'Route Discovery':<25} | {route_discovery_msgs:<8} | {'0.00%':<10}")
        print(f"{'Data Packets':<25} | {data_packets:<8} | {data_packets/total_packets*100:.2f}%" if total_packets > 0 else f"{'Data Packets':<25} | {data_packets:<8} | {'0.00%':<10}")
        print(f"{'-'*25} | {'-'*8} | {'-'*10}")
        print(f"{'Total Packets':<25} | {total_packets:<8} | {'100.00%':<10}")
        print(f"\nProtocol Efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")
        print("(Efficiency = Data Packets / Total Packets)")

    return stats


def run_simulation(
    n_nodes: int = 10,
    area_size: int = 10,
    transmission_tests: int = 3,
    interactive: bool = False,
    time_steps: int = 20,
    p_request: float = 0.3,
    p_fail: float = 0.1,
    p_new: float = 0.1,
    delay_between_steps: float = 0.0,
    hello_interval: int = 5,
    ignore_initial_route_discovery: bool = True,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
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
        hello_interval: Send hello messages every N time steps
        ignore_initial_route_discovery: Whether to reset route discovery counters after initial convergence for static networks
        seed: Random seed for deterministic behavior (global random seed should be set before calling)
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

    # Always run dynamic scenario (static mode removed)
    return run_dynamic_scenario(
        network,
        time_steps=time_steps,
        p_request=p_request,
        p_fail=p_fail,
        p_new=p_new,
        interactive=interactive,
        delay_between_steps=delay_between_steps,
        hello_interval=hello_interval,
        ignore_initial_route_discovery=ignore_initial_route_discovery,
        seed=seed,
    )


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Wireless Sensor Network Simulator with Proactive Distance Vector Protocol"
    )
    parser.add_argument(
        "--nodes", type=int, default=10, help="Number of nodes (default: 10)"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of transmission tests (default: 10)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between simulation steps in seconds (default: 0.0)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive visualizations",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Call the main simulation function
    network = scenario_main(
        n_nodes=args.nodes,
        transmission_tests=args.iterations,
        interactive=not args.no_interactive,
        random_seed=args.seed,
        delay_between_steps=args.delay,
        verbose=args.verbose,
    )
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
        "--static", action="store_true", help="Run static scenario simulation (default is dynamic)"
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
    parser.add_argument(
        "--hello-interval",
        type=int,
        default=5,
        help="Send hello messages every N time steps (0=never, 1=every step) (default: 5)",
    )
    parser.add_argument(
        "--ignore-initial-route-discovery",
        action="store_true",
        default=True,
        help="Reset route discovery counters after initial convergence for static networks (default: True)",
    )
    parser.add_argument(
        "--consider-initial-route-discovery",
        action="store_false",
        dest="ignore_initial_route_discovery",
        help="Include initial route discovery messages in efficiency calculations",
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

    # Deterministic behavior parameters
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic behavior (default: None, uses time-based seed)",
    )

    args: argparse.Namespace = parser.parse_args()

    # Extract arguments
    interactive_mode: bool = args.interactive
    dynamic_scenario: bool = not args.static  # Dynamic is default, static overrides
    evaluation_mode: bool = args.evaluation

    n_nodes: int = args.nodes
    time_steps: int = args.time_steps
    p_request: float = args.p_request
    p_fail: float = args.p_fail
    p_new: float = args.p_new
    delay_between_steps: float = args.delay
    hello_interval: int = args.hello_interval
    ignore_initial_route_discovery: bool = args.ignore_initial_route_discovery
    seed: Optional[int] = args.seed

    # Set global random seed for deterministic behavior
    if seed is not None:
        random.seed(seed)
        print(f"Using random seed: {seed} for deterministic behavior")
        logger.info(f"Using random seed: {seed} for deterministic behavior")
    else:
        # Use time-based seed (current behavior)
        time_based_seed = int(time.time() * 1000) % 10000
        random.seed(time_based_seed)
        print(f"Using time-based random seed: {time_based_seed}")
        logger.info(f"Using time-based random seed: {time_based_seed}")

    # Auto-enable dynamic scenario if user provided time-steps > 20 or non-default probabilities
    # This ensures the probability parameters actually have an effect
    if not dynamic_scenario and not evaluation_mode:
        if (time_steps != 20 or p_request != 0.3 or p_fail != 0.1 or p_new != 0.1):
            dynamic_scenario = True
            print("Auto-enabling dynamic scenario mode because time-related parameters were provided.")
            logger.info("Auto-enabling dynamic scenario mode due to provided time-related parameters")

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
        # If user specified non-default values for p_fail or p_new, use them as fixed values
        # This allows users to override the random behavior with fixed values
        eval_p_fail = p_fail if p_fail != 0.1 else None  # Use fixed if not default
        eval_p_new = p_new if p_new != 0.1 else None    # Use fixed if not default
        
        results: Dict[str, Any] = run_evaluation(  # type: ignore
            n_topologies=n_topologies,
            iterations_per_topology=iterations_per_topology,
            max_probability=max_probability,
            n_nodes=n_nodes,
            area_size=10,
            fixed_p_request=fixed_p_request,
            fixed_p_fail=eval_p_fail,
            fixed_p_new=eval_p_new,
            time_steps=time_steps,
            seed=seed,
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
            hello_interval=hello_interval,
            ignore_initial_route_discovery=ignore_initial_route_discovery,
            seed=seed,
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
    print("  --static                  : Run static scenario simulation (default is dynamic)")
    print(
        "  --time-steps=<number>     : Number of time steps for dynamic scenario (default: 20)"
    )
    print("  --p-request=<float>       : Probability of packet request (default: 0.3)")
    print("  --p-fail=<float>          : Probability of link failure (default: 0.1)")
    print("  --p-new=<float>           : Probability of a new link (default: 0.1)")
    print(
        "  --delay=<float>           : Delay between time steps in seconds (default: 1.0)"
    )
    print(
        "  --hello-interval=<number> : Send hello messages every N time steps (default: 5)"
    )
    print(
        "  --ignore-initial-route-discovery : Reset route discovery counters after initial convergence (default: True)"
    )
    print(
        "  --consider-initial-route-discovery : Include initial route discovery messages in efficiency calculations"
    )
    print("  --evaluation, -e          : Run protocol evaluation mode")
    print("  --topologies=<number>     : Number of topologies to evaluate (default: 5)")
    print("  --iterations=<number>     : Iterations per topology (default: 10)")
    print(
        "  --max-prob=<float>        : Maximum probability for random parameters p_fail and p_new (default: 0.3)"
    )
    print("  --seed=<number>           : Random seed for deterministic behavior (default: time-based)")

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
