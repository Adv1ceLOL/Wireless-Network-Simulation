from sensor_node import SensorNode
import random

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
    
    def run_distance_vector_protocol(self, max_iterations=20):
        """Run distance vector protocol until convergence or max_iterations."""
        # Initialize distance vectors
        for node in self.nodes:
            node.distance_vector = {n.node_id: (node.connections[n.node_id] if n.node_id in node.connections else (0 if n.node_id == node.node_id else float('inf'))) for n in self.nodes}
            node.routing_table = {n.node_id: (n.node_id if n.node_id in node.connections else (node.node_id if n.node_id == node.node_id else None), node.distance_vector[n.node_id]) for n in self.nodes}
        for _ in range(max_iterations):
            # Each node sends its vector to neighbors
            for node in self.nodes:
                node.send_distance_vector(self)
            # Each node updates its table
            updates = [node.update_routing_table() for node in self.nodes]
            if not any(updates):
                break