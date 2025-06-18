#!/usr/bin/env python
# test_simulator.py - Comprehensive test for wireless network simulator

import os
import sys
import time
import random
from src.core.network import SensorNetwork
from src.core.sensor_node import SensorNode
from src.reporting.report_network import generate_network_report

# Test suite for wireless network simulator
class SimulatorTestSuite:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.network = None
        self.test_results = []

    def run_tests(self):
        """Run all tests and report results"""
        print("="*70)
        print("WIRELESS SENSOR NETWORK SIMULATOR - TEST SUITE")
        print("="*70)
        print(f"Starting tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*70)
        
        # Create output directories
        os.makedirs(os.path.join("output", "reports"), exist_ok=True)
        os.makedirs(os.path.join("output", "visualizations"), exist_ok=True)
        
        # Run test cases
        self.test_node_creation()
        self.test_network_creation()
        self.test_connection_establishment()
        self.test_distance_vector_protocol()
        self.test_routing_table()
        self.test_message_transmission()
        self.test_report_generation()
        self.test_random_network_creation()
        self.test_network_connectivity()
        self.test_network_reliability()
        
        # Print summary
        self.print_summary()
        return self.passed_tests == self.total_tests
        
    def run_test(self, name, test_function):
        """Execute a test case and record results"""
        self.total_tests += 1
        start_time = time.time()
        print(f"Running test: {name}...", end="", flush=True)
        
        try:
            result = test_function()
            duration = time.time() - start_time
            status = "PASS" if result else "FAIL"
            
            if result:
                self.passed_tests += 1
                
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
    
    def test_node_creation(self):
        """Test SensorNode class creation and basic functionality"""
        def test_function():
            # Create nodes with different parameters
            node1 = SensorNode(id=1, x=5.0, y=7.0, transmission_range=3.0)
            node2 = SensorNode(id=2, x=8.0, y=9.0, transmission_range=4.0)
            
            # Verify node attributes
            assert node1.id == 1, f"Node ID is {node1.id}, expected 1"
            assert node1.x == 5.0, f"Node X is {node1.x}, expected 5.0"
            assert node1.y == 7.0, f"Node Y is {node1.y}, expected 7.0"
            assert node1.transmission_range == 3.0, f"Range is {node1.transmission_range}, expected 3.0"
            
            # Test distance calculation
            distance = node1.distance_to(node2)
            expected_distance = ((8.0 - 5.0)**2 + (9.0 - 7.0)**2)**0.5
            assert abs(distance - expected_distance) < 0.0001, f"Distance is {distance}, expected {expected_distance}"
            
            # Test string representation
            str_rep = str(node1)
            assert "Node 1" in str_rep, f"String representation does not contain node ID: {str_rep}"
            assert "5.0, 7.0" in str_rep, f"String representation does not contain coordinates: {str_rep}"
            
            # Test is_within_range method
            assert node1.is_within_range(node2) == (distance <= node1.transmission_range), \
                f"is_within_range returned incorrect result"
            
            return True
            
        return self.run_test("SensorNode Creation", test_function)
    
    def test_network_creation(self):
        """Test SensorNetwork class creation and basic functionality"""
        def test_function():
            # Create a new network
            network = SensorNetwork()
            assert len(network.nodes) == 0, f"New network should have 0 nodes, has {len(network.nodes)}"
            
            # Add nodes manually
            node1 = SensorNode(id=0, x=1.0, y=2.0, transmission_range=2.0)
            node2 = SensorNode(id=1, x=2.0, y=3.0, transmission_range=2.0)
            
            network.add_node(node1)
            network.add_node(node2)
            
            assert len(network.nodes) == 2, f"Network should have 2 nodes, has {len(network.nodes)}"
            
            # Test node retrieval
            retrieved_node = network.get_node_by_id(0)
            assert retrieved_node is not None, "Could not retrieve node with ID 0"
            assert retrieved_node.id == 0, f"Retrieved node has incorrect ID: {retrieved_node.id}"
            
            # Test nonexistent node retrieval
            assert network.get_node_by_id(999) is None, "get_node_by_id should return None for nonexistent nodes"
            
            self.network = network  # Save for later tests
            return True
            
        return self.run_test("SensorNetwork Creation", test_function)
    
    def test_connection_establishment(self):
        """Test that connections between nodes are established correctly"""
        def test_function():
            if not self.network or len(self.network.nodes) < 2:
                print("    Network not properly initialized for this test")
                return False
                
            # Establish connections
            self.network.establish_connections()
            
            # Verify connections (nodes should be close enough to connect)
            node0 = self.network.get_node_by_id(0)
            node1 = self.network.get_node_by_id(1)
            
            assert 1 in node0.connections, f"Node 0 should be connected to Node 1, connections: {node0.connections}"
            assert 0 in node1.connections, f"Node 1 should be connected to Node 0, connections: {node1.connections}"
            
            # Test symmetry of connections
            for node in self.network.nodes:
                for conn_id in node.connections:
                    conn_node = self.network.get_node_by_id(conn_id)
                    assert node.id in conn_node.connections, \
                        f"Connection from {node.id} to {conn_id} is not symmetric"
            
            return True
            
        return self.run_test("Connection Establishment", test_function)
    
    def test_distance_vector_protocol(self):
        """Test the distance vector routing protocol"""
        def test_function():
            if not self.network:
                print("    Network not properly initialized for this test")
                return False
                
            # Create a larger network with a specific topology for testing
            network = SensorNetwork()
            
            # Create a line topology: 0 -- 1 -- 2 -- 3
            network.add_node(SensorNode(id=0, x=0.0, y=0.0, transmission_range=1.5))
            network.add_node(SensorNode(id=1, x=1.0, y=0.0, transmission_range=1.5))
            network.add_node(SensorNode(id=2, x=2.0, y=0.0, transmission_range=1.5))
            network.add_node(SensorNode(id=3, x=3.0, y=0.0, transmission_range=1.5))
            
            # Establish connections
            network.establish_connections()
            
            # Run the distance vector protocol
            network.run_distance_vector_protocol()
            
            # Verify all nodes have routing tables
            for node in network.nodes:
                assert hasattr(node, 'routing_table'), f"Node {node.id} has no routing table"
                assert isinstance(node.routing_table, dict), \
                    f"Node {node.id} routing table is not a dictionary: {type(node.routing_table)}"
            
            # Check specific routing entries in our line topology
            node0 = network.get_node_by_id(0)
            node3 = network.get_node_by_id(3)
            
            # Node 0 should route to Node 3 via Node 1
            assert node0.routing_table.get(3) == 1, \
                f"Node 0 should route to Node 3 via Node 1, but routes via {node0.routing_table.get(3)}"
                
            # Node 3 should route to Node 0 via Node 2
            assert node3.routing_table.get(0) == 2, \
                f"Node 3 should route to Node 0 via Node 2, but routes via {node3.routing_table.get(0)}"
            
            self.network = network  # Save for later tests
            return True
            
        return self.run_test("Distance Vector Protocol", test_function)
    
    def test_routing_table(self):
        """Test routing table correctness"""
        def test_function():
            if not self.network or not hasattr(self.network.nodes[0], 'routing_table'):
                print("    Network routing tables not properly initialized for this test")
                return False
                
            # For each node, verify it has the expected number of entries in routing table
            for node in self.network.nodes:
                expected_entries = len(self.network.nodes) - 1  # All nodes except self
                actual_entries = len(node.routing_table)
                assert actual_entries == expected_entries, \
                    f"Node {node.id} has {actual_entries} routing entries, expected {expected_entries}"
            
            # Verify that the routing tables define valid next hops
            for node in self.network.nodes:
                for target_id, next_hop_id in node.routing_table.items():
                    # Verify next hop is a valid node
                    assert self.network.get_node_by_id(next_hop_id) is not None, \
                        f"Node {node.id} routes to {target_id} via nonexistent node {next_hop_id}"
                    
                    # Verify next hop is directly connected
                    assert next_hop_id in node.connections, \
                        f"Node {node.id} routes to {target_id} via {next_hop_id} which is not a direct connection"
            
            return True
            
        return self.run_test("Routing Table Correctness", test_function)
    
    def test_message_transmission(self):
        """Test message transmission between nodes"""
        def test_function():
            if not self.network or not hasattr(self.network.nodes[0], 'routing_table'):
                print("    Network not properly initialized for this test")
                return False
                
            # Test message from node 0 to node 3 (should go through the whole network)
            path, delay = self.network.simulate_message_transmission(0, 3, "Test message")
            
            # Verify the path exists
            assert path is not None, "Message transmission failed, no path found"
            assert len(path) > 0, "Message path is empty"
            
            # Verify the path starts at source and ends at destination
            assert path[0] == 0, f"Path should start at node 0, starts at {path[0]}"
            assert path[-1] == 3, f"Path should end at node 3, ends at {path[-1]}"
            
            # Verify each hop in the path is connected to the previous hop
            for i in range(len(path) - 1):
                current_node = self.network.get_node_by_id(path[i])
                next_node_id = path[i+1]
                assert next_node_id in current_node.connections, \
                    f"Invalid path: {path[i]} is not connected to {path[i+1]}"
            
            # Verify delay is positive and reasonable
            assert delay > 0, f"Delay should be positive, got {delay}"
            assert delay >= len(path) - 1, f"Delay {delay} is too small for path length {len(path)}"
            
            return True
            
        return self.run_test("Message Transmission", test_function)
    
    def test_report_generation(self):
        """Test network report generation"""
        def test_function():
            if not self.network:
                print("    Network not properly initialized for this test")
                return False
                
            # Generate report
            report = generate_network_report(self.network)
            
            # Verify report contains expected sections
            assert "Network Summary" in report, "Report missing Network Summary section"
            assert "Node Details" in report, "Report missing Node Details section"
            assert "Connectivity Analysis" in report, "Report missing Connectivity Analysis section"
            assert "Routing Tables" in report, "Report missing Routing Tables section"
            
            # Verify report contains information about all nodes
            for node in self.network.nodes:
                assert f"Node {node.id}" in report, f"Report does not contain information about Node {node.id}"
            
            # Write report to file
            report_file = os.path.join("output", "reports", "test_report.txt")
            with open(report_file, 'w') as f:
                f.write(report)
                
            assert os.path.exists(report_file), f"Report file {report_file} was not created"
            
            return True
            
        return self.run_test("Report Generation", test_function)
    
    def test_random_network_creation(self):
        """Test random network creation"""
        def test_function():
            # Create a new random network
            network = SensorNetwork()
            num_nodes = 10
            area_size = 10
            
            network.create_random_network(num_nodes, area_size, min_range=2.0, max_range=3.0)
            
            # Verify node count
            assert len(network.nodes) == num_nodes, \
                f"Random network has {len(network.nodes)} nodes, expected {num_nodes}"
                
            # Verify all nodes are within area bounds
            for node in network.nodes:
                assert 0 <= node.x <= area_size, f"Node {node.id} x-coordinate {node.x} is outside area bounds"
                assert 0 <= node.y <= area_size, f"Node {node.id} y-coordinate {node.y} is outside area bounds"
                
            # Verify transmission ranges are within specified bounds
            for node in network.nodes:
                assert 2.0 <= node.transmission_range <= 3.0, \
                    f"Node {node.id} transmission range {node.transmission_range} is outside specified bounds"
                    
            # Verify connections are established
            has_connections = any(len(node.connections) > 0 for node in network.nodes)
            assert has_connections, "Random network has no connections between nodes"
            
            # Save for later tests
            self.random_network = network
            return True
            
        return self.run_test("Random Network Creation", test_function)
    
    def test_network_connectivity(self):
        """Test network connectivity analysis"""
        def test_function():
            if not hasattr(self, 'random_network'):
                print("    Random network not properly initialized for this test")
                return False
                
            network = self.random_network
            network.run_distance_vector_protocol()
            
            # Count how many nodes can reach each other
            reachability_count = 0
            total_pairs = len(network.nodes) * (len(network.nodes) - 1)
            
            for source in network.nodes:
                for target in network.nodes:
                    if source.id != target.id and target.id in source.routing_table:
                        reachability_count += 1
            
            connectivity_ratio = reachability_count / total_pairs if total_pairs > 0 else 0
            print(f"    Network connectivity: {connectivity_ratio:.2%} ({reachability_count}/{total_pairs} node pairs)")
            
            # We don't necessarily fail the test if connectivity is low,
            # but we report it for informational purposes
            
            return True
            
        return self.run_test("Network Connectivity", test_function)
    
    def test_network_reliability(self):
        """Test network reliability with node failures"""
        def test_function():
            if not hasattr(self, 'random_network'):
                print("    Random network not properly initialized for this test")
                return False
                
            network = self.random_network
            original_node_count = len(network.nodes)
            
            # Pick a random node that's not critical for connectivity
            candidate_nodes = []
            for i, node in enumerate(network.nodes):
                # Skip nodes with many connections as they might be critical
                if len(node.connections) < 3:
                    candidate_nodes.append(i)
                    
            if not candidate_nodes:
                print("    No suitable nodes for removal test")
                return True
                
            # Select a random node to remove
            node_index = random.choice(candidate_nodes)
            node_id = network.nodes[node_index].id
            
            # Run DV protocol before removal to get baseline connectivity
            network.run_distance_vector_protocol()
            
            original_reachability = 0
            for source in network.nodes:
                for target in network.nodes:
                    if source.id != target.id and target.id in source.routing_table:
                        original_reachability += 1
            
            # Remove the node
            removed_node = network.nodes.pop(node_index)
            print(f"    Removed Node {removed_node.id}")
            
            # Remove connections to the removed node
            for node in network.nodes:
                if removed_node.id in node.connections:
                    node.connections.remove(removed_node.id)
            
            # Run DV protocol again to update routing
            network.run_distance_vector_protocol()
            
            # Count connectivity after removal
            new_reachability = 0
            for source in network.nodes:
                for target in network.nodes:
                    if source.id != target.id and target.id in source.routing_table:
                        new_reachability += 1
            
            # Normalize reachability to account for fewer nodes
            original_pairs = original_node_count * (original_node_count - 1)
            new_pairs = len(network.nodes) * (len(network.nodes) - 1)
            
            original_connectivity = original_reachability / original_pairs if original_pairs > 0 else 0
            new_connectivity = new_reachability / new_pairs if new_pairs > 0 else 0
            
            print(f"    Connectivity before removal: {original_connectivity:.2%}")
            print(f"    Connectivity after removal: {new_connectivity:.2%}")
            
            # If connectivity dropped dramatically, the network might be too fragile
            # but we don't fail the test for this, just report it
            
            return True
            
        return self.run_test("Network Reliability", test_function)
    
    def print_summary(self):
        """Print test results summary"""
        print("\n")
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Tests passed: {self.passed_tests}/{self.total_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print("-"*70)
        
        # Print individual test results
        for test in self.test_results:
            status_str = test["status"]
            if status_str == "PASS":
                status_str = "\033[92mPASS\033[0m"  # Green
            elif status_str == "FAIL":
                status_str = "\033[91mFAIL\033[0m"  # Red
            else:
                status_str = "\033[91mERROR\033[0m"  # Red
                
            print(f"{test['name']}: {status_str} [{test['duration']:.3f}s]")
            if test["status"] == "ERROR" and "error" in test:
                print(f"  Error: {test['error']}")
        
        # Write summary to file
        report_file = os.path.join("output", "reports", "test_summary.txt")
        with open(report_file, 'w') as f:
            f.write("WIRELESS SENSOR NETWORK SIMULATOR - TEST SUMMARY\n")
            f.write("="*70 + "\n")
            f.write(f"Tests run at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tests passed: {self.passed_tests}/{self.total_tests} ({self.passed_tests/self.total_tests*100:.1f}%)\n")
            f.write("-"*70 + "\n\n")
            
            for test in self.test_results:
                f.write(f"{test['name']}: {test['status']} [{test['duration']:.3f}s]\n")
                if test["status"] == "ERROR" and "error" in test:
                    f.write(f"  Error: {test['error']}\n")
        
        print(f"\nTest summary written to: {report_file}")

if __name__ == "__main__":
    # Create and run the test suite
    test_suite = SimulatorTestSuite()
    success = test_suite.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
