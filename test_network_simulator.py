#!/usr/bin/env python
# test_network_simulator.py - Comprehensive test for wireless network simulator

import os
import sys
import time
import random
from network import SensorNetwork
from sensor_node import SensorNode
from report_network import generate_network_report

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
                status = "PASSED"
                print(f" {status} ({duration:.2f}s)")
            else:
                status = "FAILED"
                print(f" {status} ({duration:.2f}s)")
                
            self.test_results.append({
                "name": name,
                "status": status,
                "duration": duration,
                "error": None
            })
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f" ERROR ({duration:.2f}s)")
            print(f"  Error details: {str(e)}")
            
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "duration": duration,
                "error": str(e)
            })
            return False
    
    def run_all_tests(self):
        """Run all tests and display results"""
        print("="*70)
        print("WIRELESS SENSOR NETWORK SIMULATOR - TEST SUITE")
        print("="*70)
        print(f"Starting tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*70)
        
        # Set random seed for reproducibility
        random.seed(42)
        
        # Run all tests
        self.run_test("SensorNode Creation", self.test_sensor_node)
        self.run_test("SensorNode Connections", self.test_sensor_node_connections)
        self.run_test("Network Creation", self.test_network_creation)
        self.run_test("Network Node Positioning", self.test_network_node_positioning)
        self.run_test("Network Connections", self.test_network_connections)
        self.run_test("Distance Vector Protocol", self.test_distance_vector)
        self.run_test("Message Transmission", self.test_message_transmission)
        self.run_test("Network Report Generation", self.test_report_generation)
        self.run_test("Matplotlib Visualization", self.test_matplotlib_visualization)
        self.run_test("NetworkX Visualization", self.test_networkx_visualization)
        self.run_test("Adjacency List Visualization", self.test_adjacency_visualization)
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("-"*70)
        print(f"Total tests:  {self.total}")
        print(f"Passed tests: {self.passed}")
        print(f"Failed tests: {self.total - self.passed}")
        print(f"Success rate: {self.passed/self.total:.1%}")
        print("="*70)
        
        # Return overall result
        return self.passed == self.total
    
    def test_sensor_node(self):
        """Test SensorNode basic properties"""
        node = SensorNode(node_id=1, x=2.5, y=3.5)
        return (node.node_id == 1 and 
                abs(node.x - 2.5) < 0.001 and 
                abs(node.y - 3.5) < 0.001)
    
    def test_sensor_node_connections(self):
        """Test SensorNode connection functionality"""
        node = SensorNode(node_id=1, x=2.5, y=3.5)
        node.add_connection(2, 0.5)
        node.add_connection(3, 0.75)
        
        return (2 in node.connections and 
                3 in node.connections and
                abs(node.connections[2] - 0.5) < 0.001 and
                abs(node.connections[3] - 0.75) < 0.001)
    
    def test_network_creation(self):
        """Test network creation"""
        self.network = SensorNetwork()
        self.network.create_random_network(10, 10)
        return len(self.network.nodes) == 10
    
    def test_network_node_positioning(self):
        """Test node positioning in network"""
        if not self.network:
            self.network = SensorNetwork()
            self.network.create_random_network(10, 10)
        
        area_size = 10
        for node in self.network.nodes:
            if not (0 <= node.x <= area_size and 0 <= node.y <= area_size):
                return False
        return True
    
    def test_network_connections(self):
        """Test network connections"""
        if not self.network:
            self.network = SensorNetwork()
            self.network.create_random_network(10, 10)
        
        # Check bidirectional connections
        for node in self.network.nodes:
            for neighbor_id, delay in node.connections.items():
                neighbor = self.network.get_node_by_id(neighbor_id)
                if node.node_id not in neighbor.connections:
                    return False
                if not (0 <= delay <= 1):
                    return False
        
        return True
    
    def test_distance_vector(self):
        """Test distance vector protocol"""
        if not self.network:
            self.network = SensorNetwork()
            self.network.create_random_network(10, 10)
        
        # Run the protocol
        self.network.run_distance_vector_protocol()
        
        # Check if routing tables were created
        for node in self.network.nodes:
            if not hasattr(node, 'routing_table') or not node.routing_table:
                return False
            
            # Check self-route exists
            if node.node_id not in node.routing_table:
                return False
        
        return True
    
    def test_message_transmission(self):
        """Test message transmission"""
        if not self.network:
            self.network = SensorNetwork()
            self.network.create_random_network(10, 10)
            self.network.run_distance_vector_protocol()
        
        # Try multiple transmissions to increase chance of success
        for _ in range(10):
            source_id = random.randint(0, 9)
            target_id = random.randint(0, 9)
            while target_id == source_id:
                target_id = random.randint(0, 9)
                
            path, _ = self.network.simulate_message_transmission(source_id, target_id, "Test message")
            if path:  # If any transmission succeeds
                return True
        
        return False  # No transmissions succeeded
    
    def test_report_generation(self):
        """Test report generation"""
        if not self.network:
            self.network = SensorNetwork()
            self.network.create_random_network(5, 10)
            self.network.run_distance_vector_protocol()
        
        report_file = "test_network_report.txt"
        generate_network_report(self.network, output_file=report_file)
        
        result = os.path.exists(report_file)
        
        # Check content
        if result:
            with open(report_file, 'r') as f:
                content = f.read()
                
            # Check for key sections
            has_key_sections = (
                "NETWORK OVERVIEW" in content and
                "NODE DETAILS" in content and
                "ADJACENCY MATRIX" in content and
                "NETWORK STATISTICS" in content
            )
            
            # Clean up
            try:
                os.remove(report_file)
            except:
                pass
                
            return has_key_sections
        
        return False
    
    def test_matplotlib_visualization(self):
        """Test matplotlib visualization"""
        try:
            from visualization import visualize_network_matplotlib
            
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(5, 10)
                self.network.run_distance_vector_protocol()
            
            test_file = "test_matplotlib_viz.png"
            if os.path.exists(test_file):
                os.remove(test_file)
                
            # Suppress print output
            orig_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            visualize_network_matplotlib(self.network, output_file=test_file)
            
            # Restore stdout
            sys.stdout.close()
            sys.stdout = orig_stdout
            
            result = os.path.exists(test_file)
            
            # Clean up
            if result:
                try:
                    os.remove(test_file)
                except:
                    pass
                
            return result
        except Exception as e:
            print(f"\n  Visualization error: {e}")
            return False
    
    def test_networkx_visualization(self):
        """Test networkx visualization"""
        try:
            from visualization import visualize_network_networkx
            
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(5, 10)
                self.network.run_distance_vector_protocol()
            
            test_file = "test_networkx_viz.png"
            if os.path.exists(test_file):
                os.remove(test_file)
                
            # Suppress print output
            orig_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            visualize_network_networkx(self.network, output_file=test_file)
            
            # Restore stdout
            sys.stdout.close()
            sys.stdout = orig_stdout
            
            result = os.path.exists(test_file)
            
            # Clean up
            if result:
                try:
                    os.remove(test_file)
                except:
                    pass
                
            return result
        except Exception as e:
            print(f"\n  Visualization error: {e}")
            return False
    
    def test_adjacency_visualization(self):
        """Test adjacency list visualization"""
        try:
            from visualization import visualize_adjacency_list
            
            if not self.network:
                self.network = SensorNetwork()
                self.network.create_random_network(5, 10)
                self.network.run_distance_vector_protocol()
            
            test_file = "test_adjacency_viz.png"
            if os.path.exists(test_file):
                os.remove(test_file)
                
            # Suppress print output
            orig_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            visualize_adjacency_list(self.network, output_file=test_file)
            
            # Restore stdout
            sys.stdout.close()
            sys.stdout = orig_stdout
            
            result = os.path.exists(test_file)
            
            # Clean up
            if result:
                try:
                    os.remove(test_file)
                except:
                    pass
                
            return result
        except Exception as e:
            print(f"\n  Visualization error: {e}")
            return False

if __name__ == "__main__":
    # Run all tests
    tester = NetworkSimulatorTester()
    all_tests_passed = tester.run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if all_tests_passed else 1)
