# Add this to your implementation of the SensorNetwork class in network.py

def simulate_message_transmission(self, source_id, target_id, message="Test message", verbose=True):
    """Simulate sending a message from source to target using current routing tables."""
    if verbose:
        print(f"\nSimulating message transmission from Node {source_id} to Node {target_id}")
        print(f"Message: '{message}'")
        
    path = []
    current = source_id
    
    # Trace the path from source to destination using routing tables
    while current != target_id:
        path.append(current)
        next_hop, _ = self.nodes[current].routing_table.get(target_id, (None, float('inf')))
        
        if next_hop is None or next_hop in path:
            if verbose:
                print("No path found (routing table incomplete or loop detected).")
            return None, float('inf')
            
        if verbose:
            print(f"Node {current} forwards packet to Node {next_hop}")
            
        current = next_hop
        
    path.append(target_id)
    total_delay = sum(self.nodes[path[i]].connections[path[i+1]] for i in range(len(path)-1))
    
    if verbose:
        print(f"Path found: {' -> '.join(map(str, path))}")
        print(f"Total transmission delay: {total_delay:.4f} units")
        
    return path, total_delay
