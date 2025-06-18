#!/usr/bin/env python
# test_simulator.py - Comprehensive test for wireless network simulator

import os
import sys
import time
import random
from network import SensorNetwork
from sensor_node import SensorNode
from report_network import generate_network_report

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

        # Run tests
        self.test_node_creation()
        self.test_network_creation()
        self.test_network_connections()
        self.test_distance_vector_protocol()
        self.test_routing()
        self.test_report_generation()
        self.test_visualizations()

        # Print summary
        print("\n" + "="*70)
        print(f"TEST SUMMARY: {self.passed_tests}/{self.total_tests} tests passed ({self.passed_tests/self.total_tests:.1%})")
        print("="*70)
        
        # Print detailed results
        print("\nDETAILED TEST RESULTS:")
        for i, (test_name, passed, message) in enumerate(self.test_results):
            status = "PASSED" if passed else "FAILED"
            print(f"{i+1}. {test_name}: {status}")
            if not passed:
                print(f"   Reason: {message}")

        return self.passed_tests, self.total_tests

    def register_test(self, test_name, passed, message=""):
        """Register test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        self.test_results.append((test_name, passed, message))
        return passed

    def test_node_creation(self):
        """Test sensor node creation"""
        print("\n1. Testing sensor node creation...")
        try:
            node = SensorNode(node_id=1, x=2.5, y=3.5)
            # Test basic properties
            x_valid = abs(node.x - 2.5) < 0.001
            y_valid = abs(node.y - 3.5) < 0.001
            id_valid = node.node_id == 1
            
            basic_props = x_valid and y_valid and id_valid
            self.register_test("SensorNode basic properties", 
                              basic_props,
                              f"Node properties mismatch: x={node.x}, y={node.y}, id={node.node_id}")
            
            # Test connection creation
            node.add_connection(2, 0.5)
            connection_exists = 2 in node.connections and abs(node.connections[2] - 0.5) < 0.001
            self.register_test("SensorNode connections", 
                              connection_exists, 
                              "Connection not created properly")
            
            # Test routing table initialization
            has_routing_table = hasattr(node, 'routing_table') and isinstance(node.routing_table, dict)
            self.register_test("SensorNode routing table", 
                              has_routing_table,
                              "Routing table not properly initialized")
            
            print(f"  Basic node tests completed: {node}")
            
        except Exception as e:
            self.register_test("SensorNode creation", False, str(e))
            print(f"  Error in node creation: {e}")

    def test_network_creation(self):
        """Test network creation"""
        print("\n2. Testing network creation...")
        try:
            # Create a network with random nodes
            self.network = SensorNetwork()
            n_nodes = 10
            area_size = 10
            
            self.network.create_random_network(n_nodes, area_size)
            
            # Verify node count
            correct_node_count = len(self.network.nodes) == n_nodes
            self.register_test("Network node count", 
                              correct_node_count,
                              f"Expected {n_nodes} nodes, got {len(self.network.nodes)}")
            
            # Verify node IDs
            node_ids = [node.node_id for node in self.network.nodes]
            correct_ids = set(node_ids) == set(range(n_nodes))
            self.register_test("Network node IDs", 
                              correct_ids,
                              f"Node IDs are not sequential: {node_ids}")
            
            # Verify node positions
            positions_valid = all(0 <= node.x <= area_size and 0 <= node.y <= area_size 
                                 for node in self.network.nodes)
            self.register_test("Network node positions", 
                              positions_valid,
                              "Node positions outside area bounds")
            
            print(f"  Network created with {len(self.network.nodes)} nodes")
            
        except Exception as e:
            self.register_test("Network creation", False, str(e))
            print(f"  Error in network creation: {e}")

    def test_network_connections(self):
        """Test network connections"""
        print("\n3. Testing network connections...")
        try:
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(10, 10)
            
            # Check if connections exist
            connections_exist = any(len(node.connections) > 0 for node in self.network.nodes)
            self.register_test("Network connections exist", 
                              connections_exist,
                              "No connections found in network")
            
            # Check bidirectional connections
            bidirectional = True
            error_msg = ""
            
            for node in self.network.nodes:
                for neighbor_id, delay in node.connections.items():
                    neighbor = self.network.get_node_by_id(neighbor_id)
                    if node.node_id not in neighbor.connections:
                        bidirectional = False
                        error_msg = f"Connection from {node.node_id} to {neighbor_id} is not bidirectional"
                        break
                if not bidirectional:
                    break
                    
            self.register_test("Bidirectional connections", 
                              bidirectional,
                              error_msg)
            
            # Check delay values
            valid_delays = all(0 <= delay <= 1 for node in self.network.nodes 
                              for delay in node.connections.values())
            self.register_test("Connection delay values", 
                              valid_delays,
                              "Delay values not in range [0,1]")
            
            # Count total connections
            total_connections = sum(len(node.connections) for node in self.network.nodes)
            avg_connections = total_connections / len(self.network.nodes)
            print(f"  Average connections per node: {avg_connections:.2f}")
            
        except Exception as e:
            self.register_test("Network connections test", False, str(e))
            print(f"  Error testing connections: {e}")

    def test_distance_vector_protocol(self):
        """Test distance vector protocol"""
        print("\n4. Testing distance vector protocol...")
        try:
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(10, 10)
            
            # Run the protocol
            self.network.run_distance_vector_protocol()
            
            # Check if routing tables were created
            has_routing_tables = all(hasattr(node, 'routing_table') for node in self.network.nodes)
            self.register_test("Routing tables exist", 
                              has_routing_tables,
                              "Routing tables not created for all nodes")
            
            # Check if routing tables have entries
            routing_entries_exist = all(len(node.routing_table) > 0 for node in self.network.nodes)
            self.register_test("Routing table entries", 
                              routing_entries_exist,
                              "Empty routing tables found")
            
            # Check that each node has a route to itself with cost 0
            self_routes_valid = all(node.node_id in node.routing_table and 
                                   node.routing_table[node.node_id]['cost'] == 0 
                                   for node in self.network.nodes)
            self.register_test("Self-routes in routing tables", 
                              self_routes_valid,
                              "Nodes missing route to themselves with cost 0")
            
            # Count reachable nodes
            total_routes = sum(len(node.routing_table) for node in self.network.nodes)
            avg_routes = total_routes / len(self.network.nodes)
            print(f"  Average reachable nodes per node: {avg_routes:.2f}")
            
        except Exception as e:
            self.register_test("Distance vector protocol", False, str(e))
            print(f"  Error testing distance vector protocol: {e}")

    def test_routing(self):
        """Test message routing"""
        print("\n5. Testing message routing...")
        try:
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(10, 10)
                self.network.run_distance_vector_protocol()
            
            # Try 5 random transmissions
            num_transmissions = 5
            successful = 0
            
            for i in range(num_transmissions):
                source_id = random.randint(0, len(self.network.nodes)-1)
                target_id = random.randint(0, len(self.network.nodes)-1)
                while target_id == source_id:
                    target_id = random.randint(0, len(self.network.nodes)-1)
                    
                message = f"Test message {i+1}"
                path, delay = self.network.simulate_message_transmission(source_id, target_id, message)
                
                if path:
                    successful += 1
            
            # At least one successful transmission
            self.register_test("Message routing", 
                              successful > 0,
                              f"No successful transmissions out of {num_transmissions} attempts")
            
            print(f"  Successful transmissions: {successful}/{num_transmissions}")
            
        except Exception as e:
            self.register_test("Message routing", False, str(e))
            print(f"  Error testing message routing: {e}")

    def test_report_generation(self):
        """Test report generation"""
        print("\n6. Testing report generation...")
        try:
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(10, 10)
                self.network.run_distance_vector_protocol()
            
            # Generate report
            report_file = "test_network_report.txt"
            generate_network_report(self.network, output_file=report_file)
            
            # Check if file was created
            file_exists = os.path.exists(report_file)
            self.register_test("Report file creation", 
                              file_exists,
                              f"Report file {report_file} not created")
            
            # Check file content
            if file_exists:
                with open(report_file, 'r') as f:
                    content = f.read()
                
                # Check for key sections
                has_overview = "NETWORK OVERVIEW" in content
                has_node_details = "NODE DETAILS" in content
                has_adjacency = "ADJACENCY MATRIX" in content
                has_stats = "NETWORK STATISTICS" in content
                
                all_sections = has_overview and has_node_details and has_adjacency and has_stats
                self.register_test("Report content", 
                                  all_sections,
                                  "Report missing required sections")
                
                # Clean up test file
                try:
                    os.remove(report_file)
                except:
                    pass
            
            print("  Report generation completed")
            
        except Exception as e:
            self.register_test("Report generation", False, str(e))
            print(f"  Error testing report generation: {e}")

    def test_visualizations(self):
        """Test visualization generation"""
        print("\n7. Testing visualizations...")
        
        # Remove any existing visualization files
        viz_files = [
            "test_visualization_matplotlib.png",
            "test_visualization_networkx.png",
            "test_adjacency_list.png"
        ]
        
        for file in viz_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        try:
            # Import visualization module
            try:
                from visualization import (
                    visualize_network_matplotlib,
                    visualize_network_networkx,
                    visualize_adjacency_list
                )
                import_success = True
            except ImportError as e:
                import_success = False
                self.register_test("Visualization module import", False, str(e))
                print(f"  Error importing visualization module: {e}")
                return  # Skip remaining tests if import fails
                
            self.register_test("Visualization module import", import_success)
            
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(10, 10)
                self.network.run_distance_vector_protocol()
            
            # Test matplotlib visualization
            try:
                # Redirect standard output
                orig_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w')
                
                # Override filename for test
                visualize_network_matplotlib(self.network, output_file="test_visualization_matplotlib.png")
                
                # Restore stdout
                sys.stdout.close()
                sys.stdout = orig_stdout
                
                matplotlib_success = os.path.exists("test_visualization_matplotlib.png")
                self.register_test("Matplotlib visualization", 
                                  matplotlib_success,
                                  "Matplotlib visualization file not created")
            except Exception as e:
                self.register_test("Matplotlib visualization", False, str(e))
                print(f"  Error in matplotlib visualization: {e}")
            
            # Test networkx visualization
            try:
                # Redirect standard output
                orig_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w')
                
                # Override filename for test
                visualize_network_networkx(self.network, output_file="test_visualization_networkx.png")
                
                # Restore stdout
                sys.stdout.close()
                sys.stdout = orig_stdout
                
                networkx_success = os.path.exists("test_visualization_networkx.png")
                self.register_test("NetworkX visualization", 
                                  networkx_success,
                                  "NetworkX visualization file not created")
            except Exception as e:
                self.register_test("NetworkX visualization", False, str(e))
                print(f"  Error in networkx visualization: {e}")
            
            # Test adjacency list visualization
            try:
                # Redirect standard output
                orig_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w')
                
                # Override filename for test
                visualize_adjacency_list(self.network, output_file="test_adjacency_list.png")
                
                # Restore stdout
                sys.stdout.close()
                sys.stdout = orig_stdout
                
                adjacency_success = os.path.exists("test_adjacency_list.png")
                self.register_test("Adjacency list visualization", 
                                  adjacency_success,
                                  "Adjacency list visualization file not created")
            except Exception as e:
                self.register_test("Adjacency list visualization", False, str(e))
                print(f"  Error in adjacency list visualization: {e}")
            
            # Clean up test files
            for file in viz_files:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except:
                        pass
            
            print("  Visualization tests completed")
            
        except Exception as e:
            self.register_test("Visualizations", False, str(e))
            print(f"  Error testing visualizations: {e}")

if __name__ == "__main__":
    # Seed for reproducibility
    random.seed(42)
    
    # Run tests
    test_suite = SimulatorTestSuite()
    passed, total = test_suite.run_tests()
    
    # Exit with status code based on test results
    sys.exit(0 if passed == total else 1)
