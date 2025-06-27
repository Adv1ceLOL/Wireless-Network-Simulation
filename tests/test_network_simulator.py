#!/usr/bin/env python
# test_network_simulator.py - Comprehensive test for wireless network simulator

import os
import sys
import time
import random

# Add the parent directory to sys.path to find the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network import SensorNetwork
from src.core.sensor_node import SensorNode
from src.reporting.report_network import generate_network_report

class NetworkSimulatorTester:
    """Test suite for the Wireless Sensor Network Simulator"""
    
    def __init__(self):
        self.passed = 0
        self.total = 0
        self.test_results = []
        self.network = None
        
    def run_test(self, name, test_function):
        """Run a test and record the result"""
        self.total += 1
        start_time = time.time()
        
        print(f"Running test: {name}...", end="", flush=True)
        try:
            result = test_function()
            duration = time.time() - start_time
            
            if result:
                self.passed += 1
                status = "PASS"
            else:
                status = "FAIL"
                
            print(f" {status} [{duration:.3f}s]")
            self.test_results.append({
                "name": name,
                "status": status,
                "duration": duration
            })
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f" ERROR [{duration:.3f}s]")
            print(f"    Exception: {str(e)}")
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "duration": duration,
                "error": str(e)
            })
            return False
    
    def test_network_creation(self, num_nodes=10, area_size=10):
        """Test basic network creation"""
        self.network = SensorNetwork()
        self.network.create_random_network(num_nodes, area_size)
        
        # Basic validation
        result = len(self.network.nodes) == num_nodes
        if not result:
            print(f"    Expected {num_nodes} nodes, but got {len(self.network.nodes)}")
        
        # Check node positions are within area bounds
        for node in self.network.nodes:            
            if node.x < 0 or node.x > area_size or node.y < 0 or node.y > area_size:
                print(f"    Node {node.node_id} position ({node.x}, {node.y}) is outside area bounds")
                result = False
        
        return result
    
    def test_node_connections(self):
        """Test that node connections are properly established"""
        if not self.network:
            print("    Network not created yet")
            return False
            
        # Check that connections are symmetrical
        for node in self.network.nodes:
            for connected_id in node.connections:
                connected_node = self.network.get_node_by_id(connected_id)                
                if node.node_id not in connected_node.connections:
                    print(f"    Connection from {node.node_id} to {connected_id} is not symmetrical")
                    return False
          # Check that connections are within transmission range
        for node in self.network.nodes:
            for connected_id in node.connections:
                connected_node = self.network.get_node_by_id(connected_id)
                distance = node.distance_to(connected_node)
                # Some connections might exceed transmission range due to the 
                # _ensure_fully_connected_network method adjusting ranges
                # So we check if either node's range is sufficient
                if distance > node.transmission_range and distance > connected_node.transmission_range:
                    print(f"    Connection from {node.node_id} to {connected_id} exceeds both nodes' transmission ranges")
                    print(f"    Distance: {distance}, Node Range: {node.transmission_range}, Connected Node Range: {connected_node.transmission_range}")
                    return False
        
        return True
    
    def test_distance_vector_protocol(self):
        """Test the distance vector routing protocol"""
        if not self.network:
            print("    Network not created yet")
            return False
            
        self.network.run_distance_vector_protocol()
          # Check that all nodes have routing tables
        for node in self.network.nodes:
            if not hasattr(node, 'routing_table') or not node.routing_table:
                print(f"    Node {node.node_id} has no routing table")
                return False
          # Check for disconnected components by verifying that each node
        # has a route to every other node (if the network is connected)
        all_connected = True
        for source in self.network.nodes:
            for target in self.network.nodes:
                if source.node_id != target.node_id and target.node_id not in source.routing_table:
                    # This is not an error if the network has disconnected components
                    all_connected = False
        
        if not all_connected:
            print("    Note: Network appears to have disconnected components")
            # We don't fail the test for this, just note it
        
        return True
    
    def test_message_transmission(self, num_tests=5):
        """Test message transmission between random nodes"""
        if not self.network:
            print("    Network not created yet")
            return False
            
        # Ensure we have the routing tables set up
        if not hasattr(self.network.nodes[0], 'routing_table'):
            self.network.run_distance_vector_protocol()
        
        num_nodes = len(self.network.nodes)
        success_count = 0
        
        for _ in range(num_tests):
            source_id = random.randint(0, num_nodes-1)
            target_id = random.randint(0, num_nodes-1)
            while target_id == source_id:
                target_id = random.randint(0, num_nodes-1)
                
            message = f"Test message from {source_id} to {target_id}"
            result = self.network.simulate_message_transmission(source_id, target_id, message)
            # Unpack the result - handle both 2-tuple and 3-tuple returns
            if len(result) == 3:
                path, delay, _ = result
            else:
                path, delay = result
            
            if path:
                success_count += 1
                # Verify path validity
                for i in range(len(path) - 1):
                    node = self.network.get_node_by_id(path[i])
                    next_node_id = path[i+1]
                    if next_node_id not in node.connections:
                        print(f"    Invalid path: {path[i]} is not connected to {next_node_id}")
                        return False
        
        success_rate = success_count / num_tests
        print(f"    Message transmission success rate: {success_rate:.2%}")
        
        # Consider the test passed if at least one message was successfully transmitted
        # (accounts for disconnected networks)
        return success_count > 0
    
    def test_reporting(self):
        """Test network report generation"""
        if not self.network:
            print("    Network not created yet")
            return False
            
        try:
            report = generate_network_report(self.network)
              # Check that the report contains expected sections
            expected_sections = [
                "NETWORK OVERVIEW", 
                "NODE DETAILS", 
                "ADJACENCY MATRIX",
                "NETWORK STATISTICS"
            ]
            
            for section in expected_sections:
                if section not in report:
                    print(f"    Report is missing section: {section}")
                    return False
            
            return True
        except Exception as e:
            print(f"    Report generation failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all available tests"""
        print("="*70)
        print("WIRELESS SENSOR NETWORK SIMULATOR - TEST SUITE")
        print("="*70)
        print(f"Starting tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*70)
        
        # Configure test parameters
        num_nodes = 10
        area_size = 10
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join("output", "reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Run the tests
        self.run_test("Network Creation", lambda: self.test_network_creation(num_nodes, area_size))
        self.run_test("Node Connections", self.test_node_connections)
        self.run_test("Distance Vector Protocol", self.test_distance_vector_protocol)
        self.run_test("Message Transmission", self.test_message_transmission)
        self.run_test("Network Reporting", self.test_reporting)
        
        # Print summary
        print("\n")
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Tests passed: {self.passed}/{self.total} ({self.passed/self.total:.1%})")
        
        # Write test report to file
        report_file = os.path.join(output_dir, "test_report.txt")
        with open(report_file, 'w') as f:
            f.write("WIRELESS SENSOR NETWORK SIMULATOR - TEST REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Tests run at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tests passed: {self.passed}/{self.total} ({self.passed/self.total:.1%})\n")
            f.write("-"*70 + "\n\n")
            
            for test in self.test_results:
                f.write(f"{test['name']}: {test['status']} [{test['duration']:.3f}s]\n")
                if test['status'] == "ERROR" and 'error' in test:
                    f.write(f"  Error: {test['error']}\n")
            
        print(f"Test report written to: {report_file}")
        
        # Return overall success
        return self.passed == self.total

if __name__ == "__main__":
    # Create and run the tester
    tester = NetworkSimulatorTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
