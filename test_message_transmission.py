#!/usr/bin/env python3
"""
Test script to reproduce the message transmission issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.network import SensorNetwork

def test_message_transmission():
    """Test message transmission between potentially unconnected nodes"""
    
    # Create a small network
    network = SensorNetwork()
    network.create_random_network(n=5, area_size=10)
    
    print("Running distance vector protocol...")
    iterations = network.run_distance_vector_protocol(verbose=False)
    print(f"Protocol converged after {iterations} iterations")
    
    # Test all possible pairs
    n_nodes = len(network.nodes)
    print(f"\nTesting message transmission between all pairs of {n_nodes} nodes:")
    
    for source_id in range(n_nodes):
        for target_id in range(n_nodes):
            if source_id != target_id:
                try:
                    print(f"\nTesting: Node {source_id} -> Node {target_id}")
                    path, delay, error_reason = network.simulate_message_transmission(
                        source_id, target_id, f"Test message {source_id}->{target_id}", verbose=False
                    )
                    
                    if path and error_reason is None:
                        print(f"  ✅ SUCCESS: Path = {' -> '.join(map(str, path))}, Delay = {delay:.4f}")
                    else:
                        print(f"  ❌ FAILED: {error_reason}")
                        
                except Exception as e:
                    print(f"  💥 EXCEPTION: {str(e)}")
                    import traceback
                    traceback.print_exc()
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_message_transmission()
