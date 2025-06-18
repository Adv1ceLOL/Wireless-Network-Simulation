#!/usr/bin/env python
# test_simple.py - Simple test for wireless network simulator

import os
import sys
import random
from network import SensorNetwork
from sensor_node import SensorNode
from report_network import generate_network_report

# Define test results
tests_passed = 0
total_tests = 0

def run_test(test_name, test_func):
    """Run a test and report result"""
    global tests_passed, total_tests
    total_tests += 1
    print(f"Testing: {test_name}...", end="")
    try:
        result = test_func()
        if result:
            tests_passed += 1
            print(" PASSED")
            return True
        else:
            print(" FAILED")
            return False
    except Exception as e:
        print(f" FAILED (Error: {e})")
        return False

def test_sensor_node():
    """Test basic sensor node functionality"""
    node = SensorNode(node_id=1, x=2.5, y=3.5)
    node.add_connection(2, 0.5)
    return (node.node_id == 1 and 
            abs(node.x - 2.5) < 0.001 and 
            abs(node.y - 3.5) < 0.001 and 
            2 in node.connections and 
            abs(node.connections[2] - 0.5) < 0.001)

def test_network_creation():
    """Test network creation"""
    network = SensorNetwork()
    network.create_random_network(10, 10)
    return len(network.nodes) == 10

def test_distance_vector():
    """Test distance vector protocol"""
    network = SensorNetwork()
    network.create_random_network(8, 10)
    network.run_distance_vector_protocol()
    
    # Verify routing tables exist
    for node in network.nodes:
        if not hasattr(node, 'routing_table') or not node.routing_table:
            return False
    return True

def test_message_transmission():
    """Test message transmission"""
    network = SensorNetwork()
    network.create_random_network(8, 10)
    network.run_distance_vector_protocol()
    
    # Try multiple transmissions to increase chance of success
    for _ in range(5):
        source_id = random.randint(0, 7)
        target_id = random.randint(0, 7)
        while target_id == source_id:
            target_id = random.randint(0, 7)
            
        path, _ = network.simulate_message_transmission(source_id, target_id, "Test message")
        if path:  # If any transmission succeeds
            return True
    
    return False  # No transmissions succeeded

def test_report_generation():
    """Test report generation"""
    network = SensorNetwork()
    network.create_random_network(5, 10)
    network.run_distance_vector_protocol()
    
    report_file = "test_report.txt"
    generate_network_report(network, output_file=report_file)
    
    result = os.path.exists(report_file)
    
    # Clean up
    if result:
        try:
            os.remove(report_file)
        except:
            pass
    
    return result

def test_visualization():
    """Test visualization import and functionality"""
    try:
        from visualization import (
            visualize_network_matplotlib,
            visualize_network_networkx,
            visualize_adjacency_list
        )
        
        # Create a test network
        network = SensorNetwork()
        network.create_random_network(5, 10)
        network.run_distance_vector_protocol()
        
        # Try creating test visualizations
        test_files = [
            "test_viz_matplotlib.png",
            "test_viz_networkx.png",
            "test_viz_adjacency.png"
        ]
        
        # Clean up any existing test files
        for file in test_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        # Generate visualizations
        visualize_network_matplotlib(network, output_file=test_files[0])
        visualize_network_networkx(network, output_file=test_files[1])
        visualize_adjacency_list(network, output_file=test_files[2])
        
        # Check if files were created
        all_files_created = all(os.path.exists(file) for file in test_files)
        
        # Clean up
        for file in test_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        return all_files_created
    except Exception as e:
        print(f"\n  Error in visualization: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("WIRELESS SENSOR NETWORK SIMULATOR - SIMPLE TEST SUITE")
    print("="*70)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run tests
    run_test("Sensor Node Creation", test_sensor_node)
    run_test("Network Creation", test_network_creation)
    run_test("Distance Vector Protocol", test_distance_vector)
    run_test("Message Transmission", test_message_transmission)
    run_test("Report Generation", test_report_generation)
    run_test("Visualization Import", test_visualization)
    
    # Print summary
    print("\n" + "="*70)
    print(f"TEST SUMMARY: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests:.1%})")
    print("="*70)
    
    # Exit with status code
    sys.exit(0 if tests_passed == total_tests else 1)
