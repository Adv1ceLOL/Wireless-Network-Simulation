from src.core.sensor_node import SensorNode
import random
import time

class SensorNetwork:
    """A wireless sensor network consisting of nodes with weighted connections."""
    
    def __init__(self):
        """Initialize an empty sensor network."""
        self.nodes = []
        
    def add_node(self, node):
        """Add a node to the network."""
        self.nodes.append(node)
        return node
        
    def create_random_network(self, n, area_size=10, min_range=1.0, max_range=3.0):
        """Create a network with n nodes randomly positioned with random transmission ranges.
        
        Args:
            n: Number of nodes
            area_size: Size of the square area
            min_range, max_range: Min/max transmission range for nodes
        """
        self.nodes = []
        # Reset the class-level node tracking
        SensorNode._all_nodes = []
        
        for i in range(n):
            x = random.uniform(0, area_size)
            y = random.uniform(0, area_size)
            transmission_range = random.uniform(min_range, max_range)
            node = SensorNode(node_id=i, x=x, y=y, transmission_range=transmission_range)
            self.nodes.append(node)
            
        # Generate weighted connections
        self._generate_connections()
        return self.nodes
            
    def _generate_connections(self):
        """Generate bidirectional weighted connections between nodes that can reach each other."""
        n = len(self.nodes)
        for i in range(n):
            for j in range(i + 1, n):
                node_a = self.nodes[i]
                node_b = self.nodes[j]
                if node_a.can_reach(node_b) or node_b.can_reach(node_a):
                    delay = random.uniform(0, 1)
                    node_a.add_connection(node_b.node_id, delay)
                    node_b.add_connection(node_a.node_id, delay)
                    
    def get_adjacency_matrix(self):
        """Return the adjacency matrix with delays as weights."""
        n = len(self.nodes)
        matrix = [[float('inf') for _ in range(n)] for _ in range(n)]
        
        # Fill in weights where connections exist
        for i, node in enumerate(self.nodes):
            matrix[i][i] = 0  # Set diagonal to 0
            for other_node_id, delay in node.connections.items():
                matrix[i][other_node_id] = delay
                
        return matrix
    
    def get_node_by_id(self, node_id):
        """Return node with given ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def simulate_message_transmission(self, source_id, target_id, message="Test message"):
        """Simulate sending a message from source to target using current routing tables."""
        print(f"\nSimulating message transmission from Node {source_id} to Node {target_id}")
        print(f"Message: '{message}'")
        path = []
        current = source_id
        while current != target_id:
            path.append(current)
            next_hop, _ = self.nodes[current].routing_table.get(target_id, (None, float('inf')))
            if next_hop is None or next_hop in path:
                print("No path found (routing table incomplete or loop detected).")
                return None, float('inf')
            current = next_hop
        path.append(target_id)
        total_delay = sum(self.nodes[path[i]].connections[path[i+1]] for i in range(len(path)-1))
        print(f"Path found: {' -> '.join(map(str, path))}")
        print(f"Total transmission delay: {total_delay:.4f} units")
        return path, total_delay
    
    def run_distance_vector_protocol(self, max_iterations=20, verbose=False):
        """Run the proactive distance vector protocol until convergence or max iterations.
        
        Args:
            max_iterations: Maximum number of protocol iterations
            verbose: Print detailed information during protocol execution
        
        Returns:
            Number of iterations performed
        """
        # Initialize distance vectors for all nodes
        for node in self.nodes:
            node.initialize_distance_vector(self)
            
        if verbose:
            print("\nInitial distance vectors:")
            for node in self.nodes:
                print(f"Node {node.node_id}: {node.distance_vector}")
        
        # Iteratively update distance vectors until convergence
        iteration = 0
        updates_occurred = True
        
        while updates_occurred and iteration < max_iterations:
            iteration += 1
            if verbose:
                print(f"\nIteration {iteration}")
            
            # Phase 1: All nodes send their current distance vectors to neighbors
            updates_sent = False
            for node in self.nodes:
                if node.send_distance_vector(self):
                    updates_sent = True
                    
            # If no updates were sent, we're done
            if not updates_sent:
                if verbose:
                    print("No updates sent. Protocol has converged.")
                break
                
            # Phase 2: All nodes process received updates and update their routing tables
            updates_occurred = False
            for node in self.nodes:
                if node.update_routing_table():
                    updates_occurred = True
                    if verbose:
                        print(f"Node {node.node_id} updated its routing table")
            
            # Optional: Add a small delay to make the simulation more realistic
            time.sleep(0.01)
            
        if verbose:
            print(f"\nDistance vector protocol completed after {iteration} iterations")
            print("Final routing tables:")
            for node in self.nodes:
                node.print_routing_table()
                
        return iteration
    
    def _find_shortest_path(self, source_id, target_id):
        """Find shortest path between nodes using Dijkstra's algorithm."""
        n = len(self.nodes)
        distances = {i: float('inf') for i in range(n)}
        distances[source_id] = 0
        predecessors = {i: None for i in range(n)}
        unvisited = set(range(n))
        
        while unvisited:
            current = min(unvisited, key=lambda x: distances[x])
            
            if current == target_id:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = predecessors[current]
                path.reverse()
                return path, distances[target_id]
                
            if distances[current] == float('inf'):
                break
                
            unvisited.remove(current)
            current_node = self.get_node_by_id(current)
            
            for neighbor_id, delay in current_node.connections.items():
                if neighbor_id in unvisited:
                    new_distance = distances[current] + delay
                    if new_distance < distances[neighbor_id]:
                        distances[neighbor_id] = new_distance
                        predecessors[neighbor_id] = current
        
        return None, float('inf')
    
    def handle_topology_change(self, node_a_id, node_b_id, new_delay=None, verbose=False):
        """Handle a topology change (link addition, removal, or delay change).
        
        Args:
            node_a_id, node_b_id: IDs of the nodes affected by the change
            new_delay: New delay value, or None to remove the connection
            verbose: Print detailed information during update
            
        Returns:
            Number of iterations to reconverge
        """
        node_a = self.get_node_by_id(node_a_id)
        node_b = self.get_node_by_id(node_b_id)
        
        if node_a is None or node_b is None:
            raise ValueError(f"Node with ID {node_a_id} or {node_b_id} not found")
            
        if verbose:
            if new_delay is None:
                print(f"\nRemoving connection between Node {node_a_id} and Node {node_b_id}")
            else:
                print(f"\nUpdating connection between Node {node_a_id} and Node {node_b_id} to delay {new_delay:.4f}")
        
        # Update the connection
        if new_delay is None:
            # Remove the connection
            if node_b_id in node_a.connections:
                del node_a.connections[node_b_id]
                node_a.update_needed = True
            if node_a_id in node_b.connections:
                del node_b.connections[node_a_id]
                node_b.update_needed = True
        else:
            # Add or update the connection
            node_a.connections[node_b_id] = new_delay
            node_b.connections[node_a_id] = new_delay
            node_a.update_needed = True
            node_b.update_needed = True
            
        # Re-run the distance vector protocol to update routing tables
        return self.run_distance_vector_protocol(verbose=verbose)
