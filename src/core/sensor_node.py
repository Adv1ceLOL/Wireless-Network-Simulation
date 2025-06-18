import math
import random

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
        
    def get_neighbors(self):
        """Return a list of neighbor node IDs."""
        return list(self.connections.keys())
        
    def __str__(self):
        return f"Node {self.node_id} at ({self.x:.2f}, {self.y:.2f}) with {len(self.connections)} connections"
    
    @classmethod
    def get_all_nodes(cls):
        """Return all nodes in the network."""
        return cls._all_nodes
    
    def send_distance_vector(self, network):
        """Send this node's distance vector to all neighbors."""
        for neighbor_id in self.get_neighbors():
            neighbor = network.get_node_by_id(neighbor_id)
            neighbor.receive_distance_vector(self.node_id, self.distance_vector)

    def receive_distance_vector(self, from_node_id, vector):
        """Receive a distance vector from a neighbor."""
        self.neighbor_vectors[from_node_id] = vector
        
    def update_routing_table(self):
        """Update routing table using Bellman-Ford logic."""
        updated = False
        for dest in range(len(SensorNode._all_nodes)):
            if dest == self.node_id:
                self.distance_vector[dest] = 0
                self.routing_table[dest] = (self.node_id, 0)
                continue
            min_cost = float('inf')
            next_hop = None
            for neighbor_id in self.get_neighbors():
                cost_to_neighbor = self.connections[neighbor_id]
                neighbor_vector = self.neighbor_vectors.get(neighbor_id, {})
                neighbor_cost = neighbor_vector.get(dest, float('inf'))
                total_cost = cost_to_neighbor + neighbor_cost
                if total_cost < min_cost:
                    min_cost = total_cost
                    next_hop = neighbor_id
            if self.distance_vector.get(dest, float('inf')) != min_cost:
                updated = True
            self.distance_vector[dest] = min_cost
            self.routing_table[dest] = (next_hop, min_cost)
        return updated
