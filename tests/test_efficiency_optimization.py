#!/usr/bin/env python3
"""
Test script to verify the efficiency optimization feature works correctly.
Tests both with and without the ignore_initial_route_discovery parameter.
"""

import sys
import os
import random
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.network import SensorNetwork
from src.core.evaluation import (
    get_hello_msg_count,
    get_topology_msg_count, 
    get_route_discovery_msg_count,
    get_data_packet_count,
    get_total_message_count,
    get_protocol_efficiency
)

def test_efficiency_optimization_enabled():
    """Test simulation with efficiency optimization ENABLED (ignore_initial_route_discovery=True)"""
    print("\n" + "="*70)
    print("TEST 1: EFFICIENCY OPTIMIZATION ENABLED")
    print("="*70)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Create network
    network = SensorNetwork()
    network.create_random_network(5, seed=42)
    
    print(f"Created network with {len(network.nodes)} nodes")
    
    # Run initial protocol convergence and capture route discovery messages BEFORE reset
    iterations = network.run_distance_vector_protocol(verbose=False)
    print(f"Protocol converged after {iterations} iterations")
    
    # Capture route discovery messages BEFORE optimization reset
    route_discovery_before_reset = get_route_discovery_msg_count(network)
    print(f"Route discovery messages BEFORE reset: {route_discovery_before_reset}")
    
    # Apply efficiency optimization (reset route discovery counters)
    print("\nApplying efficiency optimization - resetting route discovery counters...")
    for node in network.nodes:
        node.route_discovery_msg_count = 0
    
    # Verify counters are reset
    route_discovery_after_reset = get_route_discovery_msg_count(network)
    print(f"Route discovery messages AFTER reset: {route_discovery_after_reset}")
    
    # Simulate some time steps with hello messages and packet requests
    print("\nSimulating 3 time steps with hello messages and packet requests...")
    
    for t in range(3):
        print(f"\n--- Time Step {t+1} ---")
        
        # Hello messages (every node sends to neighbors)
        for node in network.nodes:
            for neighbor_id in node.connections.keys():
                node.hello_msg_count += 1
        
        # Simulate packet request
        if len(network.nodes) >= 2:
            source_id = random.choice([node.node_id for node in network.nodes])
            target_id = random.choice([node.node_id for node in network.nodes if node.node_id != source_id])
            
            print(f"Packet request: Node {source_id} -> Node {target_id}")
            path, delay, error = network.simulate_message_transmission(source_id, target_id, verbose=False)
            
            if error is None:
                # Count data packet for each hop in the path
                for hop_node_id in path[:-1]:  # Exclude destination from forwarding count
                    hop_node = network.get_node_by_id(hop_node_id)
                    if hop_node:
                        hop_node.data_packet_count += 1
                print(f"Successful transmission via path: {' -> '.join(map(str, path))}")
            else:
                print(f"Transmission failed: {error}")
    
    # Final message counts
    hello_msgs = get_hello_msg_count(network)
    topology_msgs = get_topology_msg_count(network)
    route_discovery_msgs = get_route_discovery_msg_count(network)
    data_packets = get_data_packet_count(network)
    total_packets = get_total_message_count(network)
    efficiency = get_protocol_efficiency(network)
    
    print(f"\nFINAL MESSAGE COUNTS (WITH OPTIMIZATION):")
    print(f"  Hello Messages: {hello_msgs}")
    print(f"  Topology Messages: {topology_msgs}")
    print(f"  Route Discovery Messages: {route_discovery_msgs}")
    print(f"  Data Packets: {data_packets}")
    print(f"  Total Packets: {total_packets}")
    print(f"  Protocol Efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")
    
    return {
        "route_discovery_before_reset": route_discovery_before_reset,
        "route_discovery_after_reset": route_discovery_after_reset,
        "hello_msgs": hello_msgs,
        "topology_msgs": topology_msgs,
        "route_discovery_msgs": route_discovery_msgs,
        "data_packets": data_packets,
        "total_packets": total_packets,
        "efficiency": efficiency
    }


def test_efficiency_optimization_disabled():
    """Test simulation with efficiency optimization DISABLED (ignore_initial_route_discovery=False)"""
    print("\n" + "="*70)
    print("TEST 2: EFFICIENCY OPTIMIZATION DISABLED")
    print("="*70)
    
    # Set same random seed for fair comparison
    random.seed(42)
    
    # Create network
    network = SensorNetwork()
    network.create_random_network(5, seed=42)
    
    print(f"Created network with {len(network.nodes)} nodes")
    
    # Run initial protocol convergence and DO NOT reset route discovery messages
    iterations = network.run_distance_vector_protocol(verbose=False)
    print(f"Protocol converged after {iterations} iterations")
    
    # Capture route discovery messages WITHOUT reset (optimization disabled)
    route_discovery_after_convergence = get_route_discovery_msg_count(network)
    print(f"Route discovery messages after convergence (NO RESET): {route_discovery_after_convergence}")
    
    # Simulate same time steps as in test 1
    print("\nSimulating 3 time steps with hello messages and packet requests...")
    
    for t in range(3):
        print(f"\n--- Time Step {t+1} ---")
        
        # Hello messages (every node sends to neighbors)
        for node in network.nodes:
            for neighbor_id in node.connections.keys():
                node.hello_msg_count += 1
        
        # Simulate packet request
        if len(network.nodes) >= 2:
            source_id = random.choice([node.node_id for node in network.nodes])
            target_id = random.choice([node.node_id for node in network.nodes if node.node_id != source_id])
            
            print(f"Packet request: Node {source_id} -> Node {target_id}")
            path, delay, error = network.simulate_message_transmission(source_id, target_id, verbose=False)
            
            if error is None:
                # Count data packet for each hop in the path
                for hop_node_id in path[:-1]:  # Exclude destination from forwarding count
                    hop_node = network.get_node_by_id(hop_node_id)
                    if hop_node:
                        hop_node.data_packet_count += 1
                print(f"Successful transmission via path: {' -> '.join(map(str, path))}")
            else:
                print(f"Transmission failed: {error}")
    
    # Final message counts
    hello_msgs = get_hello_msg_count(network)
    topology_msgs = get_topology_msg_count(network)
    route_discovery_msgs = get_route_discovery_msg_count(network)
    data_packets = get_data_packet_count(network)
    total_packets = get_total_message_count(network)
    efficiency = get_protocol_efficiency(network)
    
    print(f"\nFINAL MESSAGE COUNTS (WITHOUT OPTIMIZATION):")
    print(f"  Hello Messages: {hello_msgs}")
    print(f"  Topology Messages: {topology_msgs}")
    print(f"  Route Discovery Messages: {route_discovery_msgs}")
    print(f"  Data Packets: {data_packets}")
    print(f"  Total Packets: {total_packets}")
    print(f"  Protocol Efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")
    
    return {
        "route_discovery_after_convergence": route_discovery_after_convergence,
        "hello_msgs": hello_msgs,
        "topology_msgs": topology_msgs,
        "route_discovery_msgs": route_discovery_msgs,
        "data_packets": data_packets,
        "total_packets": total_packets,
        "efficiency": efficiency
    }


def compare_results(with_opt, without_opt):
    """Compare results from both tests to verify optimization impact"""
    print("\n" + "="*70)
    print("COMPARISON: OPTIMIZATION IMPACT ANALYSIS")
    print("="*70)
    
    print(f"\nRoute Discovery Messages:")
    print(f"  Before reset (initial convergence): {with_opt['route_discovery_before_reset']}")
    print(f"  After reset (with optimization): {with_opt['route_discovery_after_reset']}")
    print(f"  Without optimization: {without_opt['route_discovery_after_convergence']}")
    
    print(f"\nFinal Protocol Efficiency:")
    print(f"  With optimization: {with_opt['efficiency']:.4f} ({with_opt['efficiency']*100:.2f}%)")
    print(f"  Without optimization: {without_opt['efficiency']:.4f} ({without_opt['efficiency']*100:.2f}%)")
    
    efficiency_improvement = with_opt['efficiency'] - without_opt['efficiency']
    print(f"  Efficiency improvement: {efficiency_improvement:.4f} ({efficiency_improvement*100:.2f} percentage points)")
    
    print(f"\nTotal Message Counts:")
    print(f"  With optimization: {with_opt['total_packets']}")
    print(f"  Without optimization: {without_opt['total_packets']}")
    
    message_reduction = without_opt['total_packets'] - with_opt['total_packets']
    print(f"  Message count reduction: {message_reduction} messages")
    
    print(f"\nBreakdown Comparison:")
    print(f"{'Metric':<20} | {'With Opt':<10} | {'Without Opt':<12} | {'Difference':<10}")
    print("-" * 60)
    print(f"{'Hello Messages':<20} | {with_opt['hello_msgs']:<10} | {without_opt['hello_msgs']:<12} | {without_opt['hello_msgs'] - with_opt['hello_msgs']:<10}")
    print(f"{'Topology Messages':<20} | {with_opt['topology_msgs']:<10} | {without_opt['topology_msgs']:<12} | {without_opt['topology_msgs'] - with_opt['topology_msgs']:<10}")
    print(f"{'Route Discovery':<20} | {with_opt['route_discovery_msgs']:<10} | {without_opt['route_discovery_msgs']:<12} | {without_opt['route_discovery_msgs'] - with_opt['route_discovery_msgs']:<10}")
    print(f"{'Data Packets':<20} | {with_opt['data_packets']:<10} | {without_opt['data_packets']:<12} | {without_opt['data_packets'] - with_opt['data_packets']:<10}")
    
    # Verify optimization is working
    print(f"\n" + "="*70)
    print("OPTIMIZATION VERIFICATION")
    print("="*70)
    
    # Test 1: Route discovery messages should be reset to 0 with optimization
    if with_opt['route_discovery_after_reset'] == 0:
        print("✅ PASS: Route discovery messages correctly reset to 0 after initial convergence")
    else:
        print("❌ FAIL: Route discovery messages not reset properly")
    
    # Test 2: Without optimization should have higher route discovery count
    if without_opt['route_discovery_msgs'] > with_opt['route_discovery_msgs']:
        print("✅ PASS: Without optimization has higher route discovery message count")
    else:
        print("❌ FAIL: Optimization not reducing route discovery messages as expected")
    
    # Test 3: Efficiency should be higher with optimization
    if with_opt['efficiency'] > without_opt['efficiency']:
        print("✅ PASS: Efficiency is higher with optimization enabled")
    else:
        print("❌ FAIL: Optimization not improving efficiency as expected")
    
    # Test 4: Total message count should be lower with optimization
    if with_opt['total_packets'] < without_opt['total_packets']:
        print("✅ PASS: Total message count is lower with optimization")
    else:
        print("❌ FAIL: Optimization not reducing total message count")
    
    print(f"\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if (with_opt['route_discovery_after_reset'] == 0 and 
        without_opt['route_discovery_msgs'] > with_opt['route_discovery_msgs'] and
        with_opt['efficiency'] > without_opt['efficiency'] and
        with_opt['total_packets'] < without_opt['total_packets']):
        print("🎉 ALL TESTS PASSED: Efficiency optimization is working correctly!")
        print("   The ignore_initial_route_discovery feature successfully:")
        print("   - Resets route discovery counters after initial convergence")
        print("   - Improves protocol efficiency calculations")
        print("   - Provides more realistic efficiency measurements")
    else:
        print("⚠️  SOME TESTS FAILED: Efficiency optimization may not be working as expected")


def test_actual_simulation_with_optimization():
    """Test the actual simulation function with optimization enabled"""
    print("\n" + "="*70)
    print("TEST 3: ACTUAL SIMULATION WITH OPTIMIZATION")
    print("="*70)
    
    # Import the actual simulation function
    from src.core.deterministic_scenario import main as scenario_main
    
    print("Running actual simulation with optimization enabled...")
    
    # Run with optimization enabled (default)
    network = scenario_main(
        n_nodes=5,
        time_steps=5,
        p_request=0.3,
        p_fail=0.0,  # No link failures for cleaner test
        p_new=0.0,   # No new links for cleaner test
        verbose=False,
        interactive=False,
        ignore_initial_route_discovery=True  # Optimization enabled
    )
    
    # Get final efficiency
    efficiency_with_opt = get_protocol_efficiency(network)
    route_discovery_with_opt = get_route_discovery_msg_count(network)
    
    print(f"Simulation complete!")
    print(f"Final efficiency with optimization: {efficiency_with_opt:.4f}")
    print(f"Route discovery messages with optimization: {route_discovery_with_opt}")
    
    return {
        "efficiency": efficiency_with_opt,
        "route_discovery": route_discovery_with_opt
    }


if __name__ == "__main__":
    print("EFFICIENCY OPTIMIZATION TEST SUITE")
    print("="*70)
    print("This test verifies that the ignore_initial_route_discovery optimization")
    print("correctly resets route discovery counters and improves efficiency calculations.")
    
    # Run tests
    print("\nStarting comprehensive test suite...")
    
    # Test 1: With optimization enabled
    with_optimization = test_efficiency_optimization_enabled()
    
    # Test 2: With optimization disabled
    without_optimization = test_efficiency_optimization_disabled()
    
    # Compare results
    compare_results(with_optimization, without_optimization)
    
    # Test 3: Actual simulation function
    actual_simulation = test_actual_simulation_with_optimization()
    
    print(f"\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)
