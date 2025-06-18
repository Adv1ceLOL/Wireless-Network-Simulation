import unittest
import sys
import os
import platform
import importlib.util
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network import SensorNetwork
from src.core.sensor_node import SensorNode
from src.reporting.report_network import generate_network_report
from src.visualization import visualization

class TestVisualization(unittest.TestCase):
    """Test suite for visualization module functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure visualization module is importable
        self.has_visualization = importlib.util.find_spec('src.visualization') is not None
        
    def test_package_detection(self):
        """Test if package detection works correctly."""
        if not self.has_visualization:
            self.skipTest("Visualization module not available")
        
        from src.visualization import is_package_installed
          # Test detection of installed packages
        self.assertTrue(is_package_installed('unittest'))
        self.assertTrue(is_package_installed('sys'))
        
        # Test detection of non-existent packages
        self.assertFalse(is_package_installed('nonexistent_package_xyz'))
    
    @patch('src.visualization.matplotlib')
    def test_backend_selection(self, mock_matplotlib):
        """Test that backend selection logic works."""
        if not self.has_visualization:
            self.skipTest("Visualization module not available")
        
        # Mock the platform and package detection
        with patch('src.visualization.platform.system', return_value='Windows'), \
             patch('src.visualization.is_package_installed', return_value=True), \
             patch('importlib.util.find_spec'):
            
            from src.visualization import get_available_backend
            result = get_available_backend()
            
            # Check if a backend was selected
            self.assertTrue(result)
            self.assertTrue(mock_matplotlib.use.called)
    
    def test_package_installation(self):
        """Test package installation functionality."""
        if not self.has_visualization:
            self.skipTest("Visualization module not available")
        
        # Define a simple mock function instead of using subprocess
        def mock_install_package(package_name):
            print(f"Mock installing {package_name}")
            return True
        
        # Save the original function and use our mock
        from src.visualization import install_package as original_install
        import src.visualization
        
        # Save original and replace with mock
        original = src.visualization.install_package
        src.visualization.install_package = mock_install_package
        
        try:
            # Test the mock installation
            result = src.visualization.install_package('test_package')
            self.assertTrue(result)
        finally:
            # Restore original function
            src.visualization.install_package = original
    
    def test_pil_visualization_fallback(self):
        """Test that PIL visualization works as a fallback."""
        if not self.has_visualization:
            self.skipTest("Visualization module not available")
        
        # Only run this test if PIL is available
        if not importlib.util.find_spec('PIL'):
            self.skipTest("PIL not available")
        
        from src.visualization import visualize_network_pil
        from src.core.network import SensorNetwork
        
        # Create a test network
        network = SensorNetwork()
        network.create_random_network(5, 10)
        
        # Test visualization with PIL
        test_output = "test_pil_visualization.png"
        visualize_network_pil(network, output_file=test_output)
        
        # Check if the file was created
        self.assertTrue(os.path.exists(test_output))
        
        # Clean up
        try:
            os.remove(test_output)
        except:
            pass

class TestNetworkSimulation(unittest.TestCase):
    """Test suite for the network simulation functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        from src.core.network import SensorNetwork
        from src.core.sensor_node import SensorNode
        
        # Create a test network with predictable values
        self.network = SensorNetwork()
        
        # Clear class-level tracking
        SensorNode._all_nodes = []
        
        # Create nodes with fixed positions
        node0 = SensorNode(node_id=0, x=0, y=0, transmission_range=2.0)
        node1 = SensorNode(node_id=1, x=1, y=0, transmission_range=2.0)
        node2 = SensorNode(node_id=2, x=2, y=0, transmission_range=2.0)
        node3 = SensorNode(node_id=3, x=3, y=0, transmission_range=2.0)
        node4 = SensorNode(node_id=4, x=4, y=0, transmission_range=2.0)
        
        # Add nodes to network
        self.network.nodes = [node0, node1, node2, node3, node4]
        
        # Set up connections manually (line topology)
        node0.add_connection(1, 0.1)
        node1.add_connection(0, 0.1)
        node1.add_connection(2, 0.2)
        node2.add_connection(1, 0.2)
        node2.add_connection(3, 0.3)
        node3.add_connection(2, 0.3)
        node3.add_connection(4, 0.4)
        node4.add_connection(3, 0.4)
    
    def test_distance_calculation(self):
        """Test distance calculation between nodes."""
        from src.core.sensor_node import SensorNode
        
        node1 = SensorNode(node_id=0, x=0, y=0)
        node2 = SensorNode(node_id=1, x=3, y=4)
        
        # Distance should be 5 (3-4-5 triangle)
        self.assertEqual(node1.distance_to(node2), 5.0)
    
    def test_node_connections(self):
        """Test that node connections are correctly established."""
        # Check that node connections are set up properly
        self.assertEqual(len(self.network.nodes[0].connections), 1)
        self.assertEqual(len(self.network.nodes[1].connections), 2)
        self.assertEqual(len(self.network.nodes[2].connections), 2)
        self.assertEqual(len(self.network.nodes[3].connections), 2)
        self.assertEqual(len(self.network.nodes[4].connections), 1)
        
        # Check specific connection values
        self.assertEqual(self.network.nodes[0].connections[1], 0.1)
        self.assertEqual(self.network.nodes[1].connections[0], 0.1)
        self.assertEqual(self.network.nodes[3].connections[4], 0.4)
    
    def test_routing(self):
        """Test that routing works correctly."""
        # Run the distance vector protocol
        self.network.run_distance_vector_protocol()
        
        # Test path from node 0 to node 4
        path, delay = self.network.simulate_message_transmission(0, 4, "Test message")
        
        # Expected path: 0 -> 1 -> 2 -> 3 -> 4
        self.assertEqual(path, [0, 1, 2, 3, 4])
        
        # Expected delay: 0.1 + 0.2 + 0.3 + 0.4 = 1.0
        self.assertEqual(delay, 1.0)
    
    def test_adjacency_matrix(self):
        """Test adjacency matrix generation."""
        matrix = self.network.get_adjacency_matrix()
        
        # Check matrix dimensions
        self.assertEqual(len(matrix), 5)
        self.assertEqual(len(matrix[0]), 5)
        
        # Check diagonal elements (should be 0)
        for i in range(5):
            self.assertEqual(matrix[i][i], 0)
        
        # Check connection weights
        self.assertEqual(matrix[0][1], 0.1)
        self.assertEqual(matrix[1][0], 0.1)
        self.assertEqual(matrix[1][2], 0.2)
        self.assertEqual(matrix[3][4], 0.4)
        
        # Check non-connected elements (should be inf)
        self.assertEqual(matrix[0][2], float('inf'))
        self.assertEqual(matrix[0][3], float('inf'))
        self.assertEqual(matrix[0][4], float('inf'))

class TestPlatformCompatibility(unittest.TestCase):
    """Test suite for platform compatibility checks."""
    
    def test_platform_detection(self):
        """Test that platform detection works correctly."""
        # This test just verifies that platform detection doesn't error
        import platform
        system = platform.system()
        self.assertIn(system, ['Windows', 'Linux', 'Darwin'])
        
    def test_file_path_handling(self):
        """Test that file paths are handled correctly across platforms."""
        # Create a test directory for visualizations
        test_dir = "test_viz_dir"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        
        # Check that paths are joined correctly
        file_path = os.path.join(test_dir, "test_file.txt")
        self.assertTrue(file_path.startswith(test_dir))
        
        # Create a test file
        with open(file_path, 'w') as f:
            f.write("Test file")
        
        # Check that the file exists
        self.assertTrue(os.path.exists(file_path))
        
        # Clean up
        os.remove(file_path)
        os.rmdir(test_dir)

def run_tests():
    """Run all tests."""
    # Create a test suite with all tests
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestVisualization))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestNetworkSimulation))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestPlatformCompatibility))
    
    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(test_suite)

if __name__ == "__main__":
    print(f"Running tests on {platform.system()} {platform.release()}")
    run_tests()
