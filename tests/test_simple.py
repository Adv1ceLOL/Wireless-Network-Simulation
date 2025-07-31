#!/usr/bin/env python
# test_simple.py - Simple test for wireless network simulator

import os
import sys
import random

# Add the parent directory to sys.path to find the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network import SensorNetwork
from src.core.sensor_node import SensorNode
from src.reporting.report_network import generate_network_report

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
            print("PASSED")
            tests_passed += 1
        else:
            print("FAILED")
        return result
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_sensor_node_creation():
    """Test that sensor nodes can be created with proper attributes"""
    # Create a sensor node with specific attributes
    node = SensorNode(node_id=1, x=5.0, y=10.0, transmission_range=3.0)
    
    # Verify attributes
    assert node.node_id == 1, f"Node ID is {node.node_id}, expected 1"
    assert node.x == 5.0, f"Node X is {node.x}, expected 5.0"
    assert node.y == 10.0, f"Node Y is {node.y}, expected 10.0"
    assert node.transmission_range == 3.0, f"Transmission range is {node.transmission_range}, expected 3.0"
    assert isinstance(node.connections, dict), f"Initial connections should be an empty dict, got {node.connections}"
    
    return True

def test_distance_calculation():
    """Test that distance between nodes is calculated correctly"""
    # Create two nodes
    node1 = SensorNode(node_id=1, x=0.0, y=0.0, transmission_range=5.0)
    node2 = SensorNode(node_id=2, x=3.0, y=4.0, transmission_range=5.0)
    
    # Calculate distance (should be 5.0 - Pythagorean theorem)
    distance = node1.distance_to(node2)
    
    # Verify distance with small epsilon for floating point comparison
    epsilon = 0.0001
    assert abs(distance - 5.0) < epsilon, f"Distance is {distance}, expected 5.0"
    
    return True

def test_network_creation():
    """Test that a network can be created with nodes"""
    # Create a network
    network = SensorNetwork()
    
    # Add nodes manually
    network.add_node(SensorNode(node_id=0, x=0.0, y=0.0, transmission_range=2.0))
    network.add_node(SensorNode(node_id=1, x=1.0, y=1.0, transmission_range=2.0))
    network.add_node(SensorNode(node_id=2, x=2.0, y=2.0, transmission_range=2.0))
    
    # Verify node count
    assert len(network.nodes) == 3, f"Network has {len(network.nodes)} nodes, expected 3"
    
    # Verify node retrieval by ID
    node = network.get_node_by_id(1)
    assert node is not None, "Could not retrieve node with ID 1"
    assert node.node_id == 1, f"Retrieved node has ID {node.node_id}, expected 1"
    
    return True

def test_connection_establishment():
    """Test that connections between nodes are established correctly"""
    # Create a network
    network = SensorNetwork()
    
    # Add nodes with overlapping transmission ranges
    node0 = SensorNode(node_id=0, x=0.0, y=0.0, transmission_range=2.0)
    node1 = SensorNode(node_id=1, x=1.0, y=1.0, transmission_range=2.0)
    node2 = SensorNode(node_id=2, x=4.0, y=4.0, transmission_range=2.0)  # Should be out of range
    
    network.add_node(node0)
    network.add_node(node1)
    network.add_node(node2)
      # Establish connections
    network._generate_connections(ensure_connected=False)  # Don't automatically connect isolated nodes
    
    # Verify connections
    assert 1 in node0.connections, "Node 0 should be connected to Node 1"
    assert 0 in node1.connections, "Node 1 should be connected to Node 0"
    assert 2 not in node0.connections, "Node 0 should not be connected to Node 2"
    assert 2 not in node1.connections, "Node 1 should not be connected to Node 2"
    
    return True

def test_distance_vector_protocol():
    """Test the distance vector routing protocol"""
    # Create a simple network with a line topology: 0 -- 1 -- 2
    network = SensorNetwork()
    
    # Add nodes in a line
    network.add_node(SensorNode(node_id=0, x=0.0, y=0.0, transmission_range=1.5))
    network.add_node(SensorNode(node_id=1, x=1.0, y=0.0, transmission_range=1.5))
    network.add_node(SensorNode(node_id=2, x=2.0, y=0.0, transmission_range=1.5))
    
    # Establish connections
    network._generate_connections()
    
    # Run the distance vector protocol
    network.run_distance_vector_protocol()
    
    # Verify routing tables
    node0 = network.get_node_by_id(0)
    node1 = network.get_node_by_id(1)
    node2 = network.get_node_by_id(2)
    
    # Check routing table entries - format is (next_hop, cost)
    assert node0.routing_table[1][0] == 1, f"Node 0 route to Node 1 is {node0.routing_table.get(1)}, expected next hop 1"
    assert node0.routing_table[2][0] == 1, f"Node 0 route to Node 2 is {node0.routing_table.get(2)}, expected next hop 1"
    assert node1.routing_table[0][0] == 0, f"Node 1 route to Node 0 is {node1.routing_table.get(0)}, expected next hop 0"
    assert node1.routing_table[2][0] == 2, f"Node 1 route to Node 2 is {node1.routing_table.get(2)}, expected next hop 2"
    assert node2.routing_table[0][0] == 1, f"Node 2 route to Node 0 is {node2.routing_table.get(0)}, expected next hop 1"
    assert node2.routing_table[1][0] == 1, f"Node 2 route to Node 1 is {node2.routing_table.get(1)}, expected next hop 1"
    
    return True

def test_message_transmission():
    """Test message transmission between nodes"""
    # Create a network with a line topology: 0 -- 1 -- 2
    network = SensorNetwork()
    
    # Add nodes in a line
    network.add_node(SensorNode(node_id=0, x=0.0, y=0.0, transmission_range=1.5))
    network.add_node(SensorNode(node_id=1, x=1.0, y=0.0, transmission_range=1.5))
    network.add_node(SensorNode(node_id=2, x=2.0, y=0.0, transmission_range=1.5))
    
    # Establish connections
    network._generate_connections()
    
    # Run the distance vector protocol
    network.run_distance_vector_protocol()
    
    # Send a message from node 0 to node 2
    path, delay, _ = network.simulate_message_transmission(0, 2, "Test message")
    
    # Verify the path and delay
    assert path == [0, 1, 2], f"Path is {path}, expected [0, 1, 2]"
    assert delay > 0, f"Delay should be positive, got {delay}"
    
    return True

def test_network_report():
    """Test network report generation"""
    # Create a simple network
    network = SensorNetwork()
    network.create_random_network(5, 10, min_range=3.0, max_range=4.0)
    network.run_distance_vector_protocol()
    
    # Generate a report
    report = generate_network_report(network)
    
    # Verify the report is not empty and contains expected sections
    assert report, "Report should not be empty"
    assert "NETWORK OVERVIEW" in report, "Report should contain Network Overview section"
    assert "NODE DETAILS" in report, "Report should contain Node Details section"
    
    return True

def run_all_tests():
    """Run all defined tests"""
    # Make sure the output directory exists
    os.makedirs(os.path.join("output", "reports"), exist_ok=True)
    
    print("="*60)
    print("WIRELESS SENSOR NETWORK SIMULATOR - SIMPLE TESTS")
    print("="*60)
    
    # Run individual tests
    run_test("Sensor Node Creation", test_sensor_node_creation)
    run_test("Distance Calculation", test_distance_calculation)
    run_test("Network Creation", test_network_creation)
    run_test("Connection Establishment", test_connection_establishment)
    run_test("Distance Vector Protocol", test_distance_vector_protocol)
    run_test("Message Transmission", test_message_transmission)
    run_test("Network Report Generation", test_network_report)
    
    # Print summary
    print("\nTest Summary:")
    print(f"Passed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.1f}%)")
    
    # Return overall success
    return tests_passed == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
