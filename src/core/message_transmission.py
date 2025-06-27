# Add this to your implementation of the SensorNetwork class in network.py

def simulate_message_transmission(self, source_id, target_id, message="Test message", verbose=True):
    """Simulate sending a message from source to target using current routing tables."""
    try:
        if verbose:
            print(f"\nSimulating message transmission from Node {source_id} to Node {target_id}")
            print(f"Message: '{message}'")
        
        # Check if source and target nodes exist
        source_node = self.get_node_by_id(source_id)
        target_node = self.get_node_by_id(target_id)
        
        if not source_node:
            error_msg = f"Source node {source_id} does not exist"
            if verbose:
                print(error_msg)
            return [], float('inf'), error_msg
            
        if not target_node:
            error_msg = f"Target node {target_id} does not exist"
            if verbose:
                print(error_msg)
            return [], float('inf'), error_msg
            
        path = []
        current = source_id
        max_hops = len(self.nodes) + 1  # Prevent infinite loops
        
        # Trace the path from source to destination using routing tables
        while current != target_id and len(path) < max_hops:
            path.append(current)
            
            # Get current node
            current_node = self.get_node_by_id(current)
            if not current_node:
                error_msg = f"Node {current} not found during path traversal"
                if verbose:
                    print(error_msg)
                return [], float('inf'), error_msg
            
            # Get next hop from routing table
            next_hop, cost = current_node.routing_table.get(target_id, (None, float('inf')))
            
            if next_hop is None:
                error_msg = f"No path found from node {current} to target - routing table incomplete"
                if verbose:
                    print(error_msg)
                return [], float('inf'), error_msg
                
            if next_hop in path:
                error_msg = "Routing loop detected"
                if verbose:
                    print(error_msg)
                return [], float('inf'), error_msg
                
            if cost == float('inf'):
                error_msg = "No valid route to destination"
                if verbose:
                    print(error_msg)
                return [], float('inf'), error_msg
                
            if verbose:
                print(f"Node {current} forwards packet to Node {next_hop}")
                
            current = next_hop
            
        if len(path) >= max_hops:
            error_msg = "Maximum hop count exceeded"
            if verbose:
                print(error_msg)
            return [], float('inf'), error_msg
            
        path.append(target_id)
        
        # Calculate total delay using get_node_by_id for each node in path
        try:
            total_delay = 0.0
            for i in range(len(path) - 1):
                from_node = self.get_node_by_id(path[i])
                to_node_id = path[i + 1]
                
                if not from_node:
                    raise KeyError(f"Node {path[i]} not found")
                    
                if to_node_id not in from_node.connections:
                    raise KeyError(f"No connection from node {path[i]} to {to_node_id}")
                    
                total_delay += from_node.connections[to_node_id]
                
        except KeyError as e:
            error_msg = f"Link missing in path: {e}"
            if verbose:
                print(error_msg)
            return [], float('inf'), error_msg
        
        if verbose:
            print(f"Path found: {' -> '.join(map(str, path))}")
            print(f"Total transmission delay: {total_delay:.4f} units")
            
        return path, total_delay, None
        
    except Exception as e:
        error_msg = f"Transmission error: {str(e)}"
        if verbose:
            print(error_msg)
        return [], float('inf'), error_msg
