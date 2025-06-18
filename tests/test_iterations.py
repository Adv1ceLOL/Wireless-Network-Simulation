#!/usr/bin/env python
# test_iterations.py - Run multiple iterations of tests for the simulator

import os
import sys
import time
import random
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from src.core.network import SensorNetwork
from src.core.sensor_node import SensorNode
from src.reporting.report_network import generate_network_report

def run_test_iterations(num_iterations=5, nodes_range=(5, 20)):
    """Run multiple iterations of network simulation tests with varying parameters."""
    print("="*70)
    print("WIRELESS SENSOR NETWORK SIMULATOR - ITERATION TESTS")
    print("="*70)
    print(f"Starting {num_iterations} iterations at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)
    
    results = []
    
    for i in range(num_iterations):
        print(f"\nIteration {i+1}/{num_iterations}")
        print("-"*30)
        
        # Random parameters for this iteration - keep area small to ensure connections
        num_nodes = random.randint(nodes_range[0], nodes_range[1])
        area_size = 10  # Fixed area size to ensure more connections
        
        # Increase transmission range for better connectivity
        min_range = 2.0
        max_range = 4.0
        
        print(f"  Parameters: {num_nodes} nodes, {area_size}x{area_size} area")
        print(f"  Transmission range: {min_range:.1f}-{max_range:.1f}")
        
        # Time the network creation
        start_time = time.time()
        network = SensorNetwork()
        network.create_random_network(num_nodes, area_size, min_range=min_range, max_range=max_range)
        creation_time = time.time() - start_time
        
        # Count connections
        total_connections = sum(len(node.connections) for node in network.nodes)
        avg_connections = total_connections / num_nodes if num_nodes > 0 else 0
        
        print(f"  Network created with {num_nodes} nodes and {total_connections} connections")
        print(f"  Average connections per node: {avg_connections:.2f}")
        print(f"  Creation time: {creation_time:.3f} seconds")
        
        # Time the distance vector protocol
        start_time = time.time()
        network.run_distance_vector_protocol()
        dv_time = time.time() - start_time
        
        print(f"  Distance vector protocol time: {dv_time:.3f} seconds")
        
        # Test message transmission
        start_time = time.time()
        success_count = 0
        total_delay = 0
        transmission_count = min(10, num_nodes * (num_nodes - 1) // 2)
        
        for _ in range(transmission_count):
            source_id = random.randint(0, num_nodes-1)
            target_id = random.randint(0, num_nodes-1)
            while target_id == source_id:
                target_id = random.randint(0, num_nodes-1)
                
            path, delay = network.simulate_message_transmission(source_id, target_id, "Test message")
            if path:
                success_count += 1
                total_delay += delay
                
        transmission_time = time.time() - start_time
        success_rate = success_count / transmission_count if transmission_count > 0 else 0
        avg_delay = total_delay / success_count if success_count > 0 else 0
        
        print(f"  Message transmission tests: {success_count}/{transmission_count} successful ({success_rate:.1%})")
        if success_count > 0:
            print(f"  Average delay: {avg_delay:.4f} units")
        print(f"  Transmission simulation time: {transmission_time:.3f} seconds")
        
        # Record results for this iteration
        results.append({
            "iteration": i+1,
            "nodes": num_nodes,
            "area_size": area_size,
            "connections": total_connections,
            "avg_connections": avg_connections,
            "creation_time": creation_time,
            "dv_time": dv_time,
            "transmission_time": transmission_time,
            "success_rate": success_rate,
            "avg_delay": avg_delay
        })
    
    # Print overall results
    print("\n")
    print("="*70)
    print("SUMMARY OF RESULTS")
    print("="*70)
    
    avg_creation_time = sum(r["creation_time"] for r in results) / len(results)
    avg_dv_time = sum(r["dv_time"] for r in results) / len(results)
    avg_success_rate = sum(r["success_rate"] for r in results) / len(results)
    avg_delay_list = [r["avg_delay"] for r in results if r["avg_delay"] > 0]
    avg_delay = sum(avg_delay_list) / len(avg_delay_list) if avg_delay_list else 0
    
    print(f"Average network creation time: {avg_creation_time:.3f} seconds")
    print(f"Average distance vector protocol time: {avg_dv_time:.3f} seconds")
    print(f"Average message success rate: {avg_success_rate:.1%}")
    if avg_delay > 0:
        print(f"Average message delay: {avg_delay:.4f} units")
    
    return results

if __name__ == "__main__":
    # Default 5 iterations, can be overridden by command line arg
    num_iterations = 5
    if len(sys.argv) > 1:
        try:
            num_iterations = int(sys.argv[1])
        except ValueError:
            print(f"Invalid argument: {sys.argv[1]}. Using default value of {num_iterations}.")
    
    # Run the test iterations
    run_test_iterations(num_iterations)
