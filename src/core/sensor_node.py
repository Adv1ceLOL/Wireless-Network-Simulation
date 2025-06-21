import math
import random
import copy

class SensorNode:
    """A node in a wireless sensor network with position and connection capabilities."""
    
    _all_nodes = []  # Keep track of all nodes in the network
    
    def __init__(self, node_id, x=0, y=0, transmission_range=1.0):
        """Initialize a sensor node.
        
        Args:
            node_id: Unique identifier for the node
            x, y: Position coordinates
            transmission_range: Maximum distance the node can transmit
        """
        self.node_id = node_id
        self.x = x
        self.y = y
        self.transmission_range = transmission_range
        self.connections = {}  # {neighbor_node_id: delay}
        self.routing_table = {}  # {destination: (next_hop, cost)}
        self.distance_vector = {}  # {destination: cost}
        self.neighbor_vectors = {}  # {neighbor_id: their distance vector}
        self.updates_to_process = []  # [(from_node_id, distance_vector), ...]
        self.update_needed = False  # Flag to indicate if this node needs to send updates
        
        # Message counters
        self.hello_msg_count = 0  # Count of hello messages
        self.topology_msg_count = 0  # Count of topology discovery messages
        self.route_discovery_msg_count = 0  # Count of control packets for route discovery
        self.data_packet_count = 0  # Count of data packets forwarded
        
        SensorNode._all_nodes.append(self)
        
    def distance_to(self, other_node):
        """Calculate Euclidean distance to another node."""
        return math.sqrt((self.x - other_node.x)**2 + (self.y - other_node.y)**2)
    
    def can_reach(self, other_node):
        """Check if this node can reach another node based on distance and range."""
        if self is other_node:
            return False
        return self.distance_to(other_node) <= self.transmission_range
    
    def add_connection(self, other_node_id, delay):
        """Add a connection to another node with specified delay."""
        self.connections[other_node_id] = delay
        self.update_needed = True
        
    def get_neighbors(self):
        """Return a list of neighbor node IDs."""
        return list(self.connections.keys())
        
    def __str__(self):
        return f"Node {self.node_id} at ({self.x:.2f}, {self.y:.2f}) with {len(self.connections)} connections"
    
    @classmethod
    def get_all_nodes(cls):
        """Return all nodes in the network."""
        return cls._all_nodes
    
    def initialize_distance_vector(self, network):
        """Initialize the distance vector for this node."""
        n_nodes = len(network.nodes)
        self.distance_vector = {i: float('inf') for i in range(n_nodes)}
        self.distance_vector[self.node_id] = 0  # Distance to self is 0
        
        # Distance to direct neighbors is the connection delay
        for neighbor_id, delay in self.connections.items():
            self.distance_vector[neighbor_id] = delay
            
        # Initialize routing table
        self.routing_table = {}
        for dest_id in range(n_nodes):
            if dest_id == self.node_id:
                self.routing_table[dest_id] = (self.node_id, 0)            
            elif dest_id in self.connections:
                self.routing_table[dest_id] = (dest_id, self.connections[dest_id])
            else:
                self.routing_table[dest_id] = (None, float('inf'))
        
        self.update_needed = True
        
    def send_distance_vector(self, network):
        """Send this node's distance vector to all neighbors if updates are needed."""
        if self.update_needed:
            for neighbor_id in self.get_neighbors():
                neighbor = network.get_node_by_id(neighbor_id)
                neighbor.receive_distance_vector(self.node_id, copy.deepcopy(self.distance_vector))
                # Increment route discovery message count
                self.route_discovery_msg_count += 1
            self.update_needed = False
            return True
        return False

    def receive_distance_vector(self, from_node_id, vector):
        """Receive a distance vector from a neighbor and queue it for processing."""
        self.updates_to_process.append((from_node_id, vector))
        
    def process_updates(self):
        """Process all queued distance vector updates."""
        if not self.updates_to_process:
            return False
            
        updated = False
        for from_node_id, vector in self.updates_to_process:
            if self._update_distance_vector(from_node_id, vector):
                updated = True
                
        self.updates_to_process = []  # Clear processed updates
        if updated:
            self.update_needed = True
        return updated
        
    def _update_distance_vector(self, from_node_id, neighbor_vector):
        """Update distance vector based on a neighbor's vector."""
        if from_node_id not in self.connections:
            return False  # Ignore updates from non-neighbors
            
        cost_to_neighbor = self.connections[from_node_id]
        updated = False
        
        for dest_id, neighbor_cost in neighbor_vector.items():
            if dest_id == self.node_id:
                continue  # Skip self
                
            # Calculate new cost through this neighbor
            new_cost = cost_to_neighbor + neighbor_cost
            
            # Update if we found a better path
            if new_cost < self.distance_vector.get(dest_id, float('inf')):
                self.distance_vector[dest_id] = new_cost
                self.routing_table[dest_id] = (from_node_id, new_cost)
                updated = True
                
        return updated
        
    def update_routing_table(self):
        """Update routing table based on current distance vector."""
        updated = self.process_updates()
        
        # Ensure routing table matches distance vector
        for dest_id, cost in self.distance_vector.items():
            current_route = self.routing_table.get(dest_id, (None, float('inf')))
            if current_route[1] != cost:
                # Find the neighbor that gives this cost
                next_hop = None
                if dest_id == self.node_id:
                    next_hop = self.node_id
                elif dest_id in self.connections and self.connections[dest_id] == cost:
                    next_hop = dest_id
                else:
                    for neighbor_id in self.get_neighbors():
                        if neighbor_id not in self.neighbor_vectors:
                            continue
                        neighbor_cost = self.neighbor_vectors.get(neighbor_id, {}).get(dest_id, float('inf'))
                        if self.connections[neighbor_id] + neighbor_cost == cost:
                            next_hop = neighbor_id
                            break
                            
                self.routing_table[dest_id] = (next_hop, cost)
                updated = True
                
        if updated:
            self.update_needed = True
            
        return updated
        
    def print_routing_table(self):
        """Print the current routing table."""
        print(f"Routing table for Node {self.node_id}:")
        for dest_id, (next_hop, cost) in sorted(self.routing_table.items()):
            if cost == float('inf'):
                cost_str = "∞"
            else:
                cost_str = f"{cost:.4f}"
                
            if next_hop is None:
                next_hop_str = "None"
            else:
                next_hop_str = str(next_hop)
                
            print(f"  Destination: {dest_id}, Next Hop: {next_hop_str}, Cost: {cost_str}")
