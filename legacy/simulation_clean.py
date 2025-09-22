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
    """Count all route discovery messages across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        count += getattr(node, "route_discovery_msg_count", 0)  # type: ignore
    return count


def get_data_packet_count(network: SensorNetwork) -> int:
    """Count all data packets across all nodes"""
    count: int = 0
    for node in network.nodes:  # type: ignore
        count += getattr(node, "data_packet_count", 0)  # type: ignore
    return count


def get_total_message_count(network: SensorNetwork) -> int:
    """Count all messages across all nodes"""
    return (get_hello_msg_count(network) + 
            get_topology_msg_count(network) + 
            get_route_discovery_msg_count(network) + 
            get_data_packet_count(network))


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
    
    print("\nSimulation complete!")
    print("Network report is saved in the output/reports directory.")
    print("Visualization files are saved in the output/visualizations directory.")
