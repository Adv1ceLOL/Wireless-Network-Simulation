#!/usr/bin/env python3
"""
Deterministic scenario runner for wireless sensor network simulation.
This module contains the main simulation logic for dynamic scenarios only.
"""

import logging
import random
import os
import platform
from typing import List, Tuple, Optional

from src.core.network import SensorNetwork
from src.reporting.report_network import generate_network_report
from src.core.evaluation import (
    get_hello_msg_count,
    get_topology_msg_count, 
    get_route_discovery_msg_count,
    get_data_packet_count,
    get_total_message_count,
)

logger = logging.getLogger(__name__)


def main(
    n_nodes: int = 10,
    interactive: bool = True,
    random_seed: Optional[int] = None,
    delay_between_steps: float = 0.0,
    verbose: bool = False,
    ignore_initial_route_discovery: bool = True,
    time_steps: int = 100,
    p_request: float = 0.5,
    p_fail: float = 0.1,
    p_new: float = 0.1,
    hello_interval: int = 1,
) -> SensorNetwork:
    """
    Main simulation function for dynamic wireless sensor network scenarios.
    
    Args:
        n_nodes: Number of nodes in the network
        interactive: Whether to enable interactive visualizations
        random_seed: Random seed for reproducibility
        delay_between_steps: Delay between simulation steps (default: 0.0)
        verbose: Enable verbose logging
        ignore_initial_route_discovery: Whether to reset route discovery counters after initial convergence
        time_steps: Number of time steps to simulate in dynamic scenario
        p_request: Probability of packet request per time step
        p_fail: Probability of link failure per time step  
        p_new: Probability of new link per time step
        hello_interval: Interval for sending hello messages (1 = every time step)
        
    Returns:
        The configured sensor network
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
        
    if random_seed is not None:
        random.seed(random_seed)
        logger.info(f"Random seed set to {random_seed}")

    logger.info("Starting dynamic wireless sensor network simulation")
    logger.info(f"Configuration: {n_nodes} nodes, {time_steps} time steps, delay={delay_between_steps}s")
    logger.info(f"Dynamic parameters: p_request={p_request}, p_fail={p_fail}, p_new={p_new}")

    # Create network with dynamic scenario (always True now)
    network = SensorNetwork()
    network.create_random_network(n_nodes, seed=random_seed)

    # Run initial protocol convergence
    iterations: int = network.run_distance_vector_protocol(verbose=verbose)
    print(f"Protocol converged after {iterations} iterations")

    # EFFICIENCY OPTIMIZATION: Reset route discovery counters after initial convergence
    if ignore_initial_route_discovery:
        logger.debug("Resetting route discovery counters after initial convergence for efficiency analysis")
        for node in network.nodes:
            node.route_discovery_msg_count = 0

    # Print initial network information
    print(f"\nNetwork created with {len(network.nodes)} nodes:")
    for node in network.nodes:
        print(f"  {node}")
        neighbors: List[str] = [
            f"Node {n_id} (delay: {delay:.3f})"
            for n_id, delay in node.connections.items()
        ]
        if neighbors:
            print(f"    Connected to: {', '.join(neighbors)}")

    # Now run the ACTUAL dynamic simulation with time steps
    print(f"\n{'-' * 60}")
    print(f"DYNAMIC SIMULATION: {time_steps} time steps")
    print(f"p_request={p_request}, p_fail={p_fail}, p_new={p_new}")
    print(f"{'-' * 60}")
    
    successful_transmissions = 0
    total_delay = 0.0
    total_requests = 0
    total_link_failures = 0
    total_new_links = 0
    
    for t in range(time_steps):
        print(f"\n--- Time Step {t+1}/{time_steps} ---")
        
        # 1. HELLO MESSAGES: Nodes send hello messages to neighbors every hello_interval steps
        if t % hello_interval == 0:
            hello_count = 0
            for node in network.nodes:
                # Send hello to all neighbors
                for neighbor_id in node.connections.keys():
                    node.hello_msg_count += 1
                    hello_count += 1
                    if verbose:
                        print(f"Node {node.node_id} sends hello to Node {neighbor_id}")
            print(f"Sent {hello_count} hello messages")
        
        # 2. TOPOLOGY CHANGES: Apply link failures and new links
        
        # Link failure with probability p_fail
        current_links = network.get_all_links()
        if current_links and random.random() < p_fail:
            # Remove a random link
            link_to_remove = random.choice(current_links)
            node_a, node_b, delay = link_to_remove
            print(f"LINK FAILURE: Removing link {node_a} <-> {node_b} (delay: {delay:.3f})")
            
            # Remove the connection
            network.nodes[node_a].connections.pop(node_b, None)
            network.nodes[node_b].connections.pop(node_a, None)
            total_link_failures += 1
            
            # Trigger routing update
            reconverge_iterations = network.handle_topology_change(node_a, node_b, new_delay=None, verbose=False)
            print(f"Routing reconverged in {reconverge_iterations} iterations")
        
        # New link with probability p_new
        if random.random() < p_new:
            # Add a new random link between two nodes that aren't already connected
            attempts = 0
            max_attempts = 20
            while attempts < max_attempts:
                node_a = random.randint(0, n_nodes - 1)
                node_b = random.randint(0, n_nodes - 1)
                if node_a != node_b and node_b not in network.nodes[node_a].connections:
                    # Create new link with random delay between 0 and 1
                    new_delay = random.uniform(0.0, 1.0)
                    print(f"NEW LINK: Adding link {node_a} <-> {node_b} (delay: {new_delay:.3f})")
                    
                    # Add the bidirectional connection
                    network.nodes[node_a].connections[node_b] = new_delay
                    network.nodes[node_b].connections[node_a] = new_delay
                    total_new_links += 1
                    
                    # Trigger routing update
                    reconverge_iterations = network.handle_topology_change(node_a, node_b, new_delay=new_delay, verbose=False)
                    print(f"Routing reconverged in {reconverge_iterations} iterations")
                    break
                attempts += 1
            
            if attempts >= max_attempts:
                print("Could not add new link (all possible connections exist or too many attempts)")
        
        # 3. PACKET REQUESTS: Generate packet transmission requests with probability p_request
        if random.random() < p_request:
            # Generate random source and destination
            source_id = random.randint(0, n_nodes - 1)
            target_id = random.randint(0, n_nodes - 1)
            while target_id == source_id:
                target_id = random.randint(0, n_nodes - 1)
            
            message = f"Data packet at time {t+1}"
            total_requests += 1
            
            print(f"PACKET REQUEST: Node {source_id} -> Node {target_id}")
            result = network.simulate_message_transmission(source_id, target_id, message, verbose=False)
            path, delay, error = result
            
            if path:
                successful_transmissions += 1
                total_delay += delay
                print(f"SUCCESS: Path {' -> '.join(map(str, path))}, delay: {delay:.4f}")
                
                # Count data packet forwards (each hop except the source)
                for i in range(len(path) - 1):
                    network.nodes[path[i]].data_packet_count += 1
            else:
                print(f"FAILED: {error}")
        
        # Add small delay between steps if requested
        if delay_between_steps > 0:
            import time
            time.sleep(delay_between_steps)

    # Print summary
    print(f"\n{'-' * 60}")
    print("DYNAMIC SIMULATION SUMMARY:")
    print(f"  Time steps simulated: {time_steps}")
    print(f"  Total packet requests: {total_requests}")
    print(f"  Successful transmissions: {successful_transmissions}")
    print(f"  Failed transmissions: {total_requests - successful_transmissions}")
    if successful_transmissions > 0:
        print(f"  Average delay: {total_delay/successful_transmissions:.4f} units")
    print(f"  Success rate: {successful_transmissions/max(1, total_requests):.1%}")
    print(f"  Link failures: {total_link_failures}")
    print(f"  New links added: {total_new_links}")
    print(f"  Final network links: {len(network.get_all_links())}")

    # Print message counters
    print("\nMessage Exchange Counters:")
    print(f"  Hello Messages: {get_hello_msg_count(network)}")
    print(f"  Topology Discovery Messages: {get_topology_msg_count(network)}")
    print(f"  Route Discovery Control Packets: {get_route_discovery_msg_count(network)}")
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

    # Generate detailed network report
    print("\nGenerating detailed network report...")
    report_dir = os.path.join("output", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, "network_report.txt")
    generate_network_report(network, output_file=report_file)

    # Handle visualization
    if interactive:
        try:
            from src.visualization.visualization import visualize_network

            print("\nGenerating interactive network visualizations...")
            logger.info("Generating interactive network visualizations")
            visualize_network(network, interactive=True)
        except ImportError as e:
            print(f"\nInteractive visualization module not available: {e}")
            print("Continuing without interactive visualizations.")
            logger.warning(f"Interactive visualization module not available: {e}")

            print("To enable visualizations, you can manually install the packages (pip install -r requirements.txt)")

            if platform.system() == "Windows":
                print("    Make sure you have tkinter installed (comes with standard Python installation)")
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
                from src.visualization.visualization import visualize_network

                visualize_network(network, interactive=False)
            except Exception as e2:
                print(f"Visualization failed: {e2}")
                logger.error(f"Visualization failed: {e2}")

    return network
