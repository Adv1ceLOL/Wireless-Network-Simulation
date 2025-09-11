#!/usr/bin/env python3
"""
Test script to analyze protocol efficiency issues and verify fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
from src.core.network import SensorNetwork
from simulation import run_dynamic_scenario

def test_hello_message_counting():
    """Test if hello message counting is correct."""
    print("=" * 60)
    print("TEST 1: Hello Message Counting")
    print("=" * 60)
    
    # Create a small network
    network = SensorNetwork()
    network.create_random_network(5, area_size=5, seed=42)
    
    print(f"Network has {len(network.nodes)} nodes")
    total_connections = sum(len(node.connections) for node in network.nodes) // 2  # Divide by 2 because connections are bidirectional
    print(f"Network has {total_connections} bidirectional links")
    
    # Reset counters
    for node in network.nodes:
        node.hello_msg_count = 0
    
    # Simulate hello message exchange (current implementation)
    hello_count_current = 0
    for node in network.nodes:
        hello_msgs = len(node.connections)  # Current implementation - wrong!
        node.hello_msg_count += hello_msgs
        hello_count_current += hello_msgs
    
    # What it should be (1 hello per node)
    hello_count_correct = len(network.nodes)
    
    print(f"Current implementation counts: {hello_count_current} hello messages")
    print(f"Correct implementation should count: {hello_count_correct} hello messages")
    print(f"Overhead ratio: {hello_count_current / hello_count_correct:.2f}x")
    
    return hello_count_current, hello_count_correct

def test_route_discovery_overhead():
    """Test route discovery message overhead during topology changes."""
    print("\n" + "=" * 60)
    print("TEST 2: Route Discovery Overhead")
    print("=" * 60)
    
    # Create a small network and run initial convergence
    network = SensorNetwork()
    network.create_random_network(10, area_size=8, seed=42)
    
    # Reset all counters
    for node in network.nodes:
        node.route_discovery_msg_count = 0
        node.hello_msg_count = 0
        node.topology_msg_count = 0
        node.data_packet_count = 0
    
    print("Running initial convergence...")
    initial_iterations = network.run_distance_vector_protocol(verbose=False)
    print(f"Initial convergence took {initial_iterations} iterations")
    
    # Count route discovery messages after initial convergence
    initial_route_msgs = sum(node.route_discovery_msg_count for node in network.nodes)
    print(f"Initial convergence generated {initial_route_msgs} route discovery messages")
    
    # Reset counters
    for node in network.nodes:
        node.route_discovery_msg_count = 0
    
    # Simulate a single topology change
    links = network.get_all_links()
    if links:
        node_a_id, node_b_id, _ = links[0]
        print(f"Removing link between Node {node_a_id} and Node {node_b_id}")
        
        reconverge_iterations = network.handle_topology_change(node_a_id, node_b_id, new_delay=None, verbose=False)
        print(f"Reconvergence took {reconverge_iterations} iterations")
        
        reconverge_route_msgs = sum(node.route_discovery_msg_count for node in network.nodes)
        print(f"Single topology change generated {reconverge_route_msgs} route discovery messages")
        
        return initial_route_msgs, reconverge_route_msgs, initial_iterations, reconverge_iterations
    
    return 0, 0, 0, 0

def test_small_dynamic_simulation():
    """Test a small dynamic simulation to verify the issues."""
    print("\n" + "=" * 60)
    print("TEST 3: Small Dynamic Simulation")
    print("=" * 60)
    
    # Create small network
    network = SensorNetwork()
    network.create_random_network(5, area_size=5, seed=42)
    
    # Run short simulation with high change probability
    stats = run_dynamic_scenario(
        network,
        time_steps=10,
        p_request=0.5,
        p_fail=0.3,
        p_new=0.3,
        hello_interval=1,  # Send hello every step
        verbose=False
    )
    
    print(f"Time steps: {10}")
    print(f"Topology changes: {stats['links_removed'] + stats['links_added']}")
    print(f"Hello exchanges: {stats['hello_exchanges']}")
    print(f"Expected hello messages (5 nodes × 10 steps): {5 * 10}")
    print(f"Actual hello messages: {sum(node.hello_msg_count for node in network.nodes)}")
    print(f"Route discovery messages: {sum(node.route_discovery_msg_count for node in network.nodes)}")
    print(f"Data packets: {sum(node.data_packet_count for node in network.nodes)}")
    
    total_messages = (sum(node.hello_msg_count for node in network.nodes) + 
                     sum(node.topology_msg_count for node in network.nodes) +
                     sum(node.route_discovery_msg_count for node in network.nodes) +
                     sum(node.data_packet_count for node in network.nodes))
    
    efficiency = sum(node.data_packet_count for node in network.nodes) / total_messages if total_messages > 0 else 0
    print(f"Protocol efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")

def analyze_large_simulation_issues():
    """Analyze what causes the issues in large simulations."""
    print("\n" + "=" * 60)
    print("ANALYSIS: Large Simulation Issues")
    print("=" * 60)
    
    # Your simulation parameters
    nodes = 50
    time_steps = 10000
    hello_interval = 1
    p_fail = 0.1
    p_new = 0.1
    
    # Estimate expected hello messages
    expected_hello_per_step = nodes  # 1 per node
    expected_total_hello = expected_hello_per_step * time_steps
    
    # Your actual results
    actual_hello = 2067220
    actual_route_discovery = 3113686
    topology_changes = 1022 + 971  # links removed + added
    
    print(f"Network: {nodes} nodes, {time_steps} time steps")
    print(f"Expected hello messages: {expected_total_hello:,}")
    print(f"Actual hello messages: {actual_hello:,}")
    print(f"Hello overhead ratio: {actual_hello / expected_total_hello:.2f}x")
    
    # Estimate average node degree
    estimated_avg_degree = actual_hello / (time_steps + topology_changes)  # Approximate
    print(f"Estimated average node degree: {estimated_avg_degree:.1f}")
    
    # Route discovery analysis
    print(f"\nRoute discovery messages: {actual_route_discovery:,}")
    print(f"Topology changes: {topology_changes}")
    print(f"Route discovery per topology change: {actual_route_discovery / topology_changes:.0f}")
    print(f"This suggests excessive reconvergence iterations or inefficient message counting")

if __name__ == "__main__":
    print("Protocol Efficiency Analysis")
    print("Testing issues with current implementation...\n")
    
    # Run tests
    test_hello_message_counting()
    test_route_discovery_overhead()
    test_small_dynamic_simulation()
    analyze_large_simulation_issues()
    
    print("\n" + "=" * 60)
    print("CONCLUSIONS")
    print("=" * 60)
    print("Issue #1: Hello messages count connections instead of nodes")
    print("  - Fix: Count 1 hello per node, not per connection")
    print("\nIssue #2: Route discovery messages accumulate excessively")
    print("  - Fix: Optimize distance vector protocol efficiency")
    print("\nIssue #3: Frequent topology changes cause massive reconvergence")
    print("  - Fix: Consider more efficient routing protocols or dampening")
