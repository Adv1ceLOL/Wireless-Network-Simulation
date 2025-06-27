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
        
        The network created will have the following properties:
        1. No isolated nodes: Every node will have at least one connection
        2. Fully connected: There will be a path between any two nodes
        
        Args:
            n: Number of nodes
            area_size: Size of the square area
            min_range, max_range: Min/max transmission range for nodes
            
        Returns:
            List of created nodes
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
        
        # Ensure no isolated nodes (nodes without connections)
        self._ensure_no_isolated_nodes()
        
        # Ensure the network is fully connected (any node can reach any other)
        self._ensure_fully_connected_network()
                    
    def _ensure_no_isolated_nodes(self):
        """Ensure that every node has at least one connection."""
        isolated_nodes = []
        
        # Find all isolated nodes
        for node in self.nodes:
            if len(node.connections) == 0:
                isolated_nodes.append(node)
        
        if not isolated_nodes:
            return  # No isolated nodes, nothing to do
            
        print(f"Found {len(isolated_nodes)} isolated nodes, connecting them to the network...")
        
        # For each isolated node, find the closest non-isolated node and connect them
        for isolated_node in isolated_nodes:
            closest_node = None
            min_distance = float('inf')
            
            # Find the closest non-isolated node
            for other_node in self.nodes:
                if other_node is isolated_node or other_node in isolated_nodes:
                    continue  # Skip self and other isolated nodes
                    
                distance = isolated_node.distance_to(other_node)
                if distance < min_distance:
                    min_distance = distance
                    closest_node = other_node
            
            # If there are no non-isolated nodes (all nodes are isolated),
            # connect to another isolated node instead
            if closest_node is None and len(isolated_nodes) > 1:
                for other_node in isolated_nodes:
                    if other_node is isolated_node:
                        continue
                        
                    distance = isolated_node.distance_to(other_node)
                    if distance < min_distance:
                        min_distance = distance
                        closest_node = other_node
            
            # If we found a node to connect to, create a bidirectional connection
            if closest_node is not None:
                # Increase the transmission range of both nodes to reach each other
                distance = isolated_node.distance_to(closest_node)
                isolated_node.transmission_range = max(isolated_node.transmission_range, distance * 1.1)
                closest_node.transmission_range = max(closest_node.transmission_range, distance * 1.1)
                
                # Create the connection with a random delay
                delay = random.uniform(0, 1)
                isolated_node.add_connection(closest_node.node_id, delay)
                closest_node.add_connection(isolated_node.node_id, delay)
                
                print(f"Connected isolated Node {isolated_node.node_id} to Node {closest_node.node_id} (distance: {distance:.2f})")
            else:
                print(f"Warning: Could not find a suitable connection for Node {isolated_node.node_id}")
        
        # Recursively check again in case there are still isolated nodes
        # (This could happen in edge cases where all nodes were initially isolated)
        still_isolated = [node for node in self.nodes if len(node.connections) == 0]
        if still_isolated:
            print(f"There are still {len(still_isolated)} isolated nodes, attempting to connect them...")
            self._ensure_no_isolated_nodes()

    def _is_network_fully_connected(self):
        """Check if the network is fully connected (any node can reach any other node).
        
        Returns:
            bool: True if the network is fully connected, False otherwise
        """
        if not self.nodes:
            return True  # Empty network is considered connected
            
        # Use breadth-first search to check connectivity
        n = len(self.nodes)
        visited = set()
        
        # Start BFS from the first node
        queue = [0]  # Start with node 0
        visited.add(0)
        
        while queue:
            current = queue.pop(0)
            current_node = self.nodes[current]
            
            for neighbor_id in current_node.connections.keys():
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)
        
        # If all nodes are visited, the network is fully connected
        return len(visited) == n
        
    def _ensure_fully_connected_network(self):
        """Ensure the network is fully connected by identifying disconnected components
        and adding links between them.
        """
        if self._is_network_fully_connected():
            return  # Network is already fully connected
            
        print("Network is not fully connected. Identifying disconnected components...")
        
        # Identify all connected components using DFS
        n = len(self.nodes)
        components = []
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
                
            # Find a new component
            component = set()
            stack = [i]
            
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                    
                component.add(current)
                visited.add(current)
                current_node = self.nodes[current]
                
                for neighbor_id in current_node.connections.keys():
                    if neighbor_id not in component:
                        stack.append(neighbor_id)
            
            components.append(component)
        
        print(f"Found {len(components)} disconnected components in the network")
        
        # Connect each component to the next one
        for i in range(len(components) - 1):
            # Find the closest pair of nodes between components i and i+1
            closest_pair = None
            min_distance = float('inf')
            
            for node_id_1 in components[i]:
                for node_id_2 in components[i + 1]:
                    node_1 = self.nodes[node_id_1]
                    node_2 = self.nodes[node_id_2]
                    distance = node_1.distance_to(node_2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_pair = (node_id_1, node_id_2)
            
            if closest_pair:
                node_1_id, node_2_id = closest_pair
                node_1 = self.nodes[node_1_id]
                node_2 = self.nodes[node_2_id]
                
                # Increase transmission range if needed
                distance = node_1.distance_to(node_2)
                node_1.transmission_range = max(node_1.transmission_range, distance * 1.1)
                node_2.transmission_range = max(node_2.transmission_range, distance * 1.1)
                
                # Create a bidirectional connection
                delay = random.uniform(0, 1)
                node_1.add_connection(node_2_id, delay)
                node_2.add_connection(node_1_id, delay)
                
                print(f"Connected component {i} to component {i+1} by linking Node {node_1_id} to Node {node_2_id} (distance: {distance:.2f})")
        
        # Verify that the network is now fully connected
        if not self._is_network_fully_connected():
            print("Warning: Network is still not fully connected after attempting to connect components")
            # Try again with a more aggressive approach
            self._connect_all_components()
            
    def _connect_all_components(self):
        """A more aggressive approach to connect all components by connecting each
        component to all other components.
        """
        print("Using more aggressive approach to connect all components...")
        
        # Identify all connected components using DFS
        n = len(self.nodes)
        components = []
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
                
            # Find a new component
            component = set()
            stack = [i]
            
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                    
                component.add(current)
                visited.add(current)
                current_node = self.nodes[current]
                
                for neighbor_id in current_node.connections.keys():
                    if neighbor_id not in component:
                        stack.append(neighbor_id)
            
            components.append(component)
        
        # For each pair of components, connect the closest nodes
        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                # Find the closest pair of nodes between components i and j
                closest_pair = None
                min_distance = float('inf')
                
                for node_id_1 in components[i]:
                    for node_id_2 in components[j]:
                        node_1 = self.nodes[node_id_1]
                        node_2 = self.nodes[node_id_2]
                        distance = node_1.distance_to(node_2)
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_pair = (node_id_1, node_id_2)
                
                if closest_pair:
                    node_1_id, node_2_id = closest_pair
                    node_1 = self.nodes[node_1_id]
                    node_2 = self.nodes[node_2_id]
                    
                    # Increase transmission range if needed
                    distance = node_1.distance_to(node_2)
                    node_1.transmission_range = max(node_1.transmission_range, distance * 1.1)
                    node_2.transmission_range = max(node_2.transmission_range, distance * 1.1)
                    
                    # Create a bidirectional connection
                    delay = random.uniform(0, 1)
                    node_1.add_connection(node_2_id, delay)
                    node_2.add_connection(node_1_id, delay)
                    
                    print(f"Connected component {i} to component {j} by linking Node {node_1_id} to Node {node_2_id} (distance: {distance:.2f})")
        
        # Final check
        if not self._is_network_fully_connected():
            print("Warning: Network is still not fully connected after aggressive connection attempt")
        else:
            print("Network is now fully connected")
                    
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
    
    def get_all_links(self):
        """Return a list of all links in the network as (node_a_id, node_b_id, delay) tuples."""
        links = []
        for i, node in enumerate(self.nodes):
            for neighbor_id, delay in node.connections.items():
                # Only add each link once (when i < neighbor_id)
                if i < neighbor_id:
                    links.append((i, neighbor_id, delay))
        return links
        
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
                return None, float('inf'), "No path found (routing table incomplete or loop detected)"
                
            if verbose:
                print(f"Node {current} forwards packet to Node {next_hop}")
                
            current = next_hop
            
        path.append(target_id)
        total_delay = sum(self.nodes[path[i]].connections[path[i+1]] for i in range(len(path)-1))
        
        if verbose:
            print(f"Path found: {' -> '.join(map(str, path))}")
            print(f"Total transmission delay: {total_delay:.4f} units")
            
        return path, total_delay, None
    
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
    
    def run_hello_message_exchange(self, verbose=False):
        """Run a round of hello message exchange where all nodes send hello messages to neighbors.
        
        Args:
            verbose: Whether to print detailed information
            
        Returns:
            Total number of hello messages exchanged
        """
        total_messages = 0
        
        if verbose:
            print("\nRunning hello message exchange across the network...")
            
        for node in self.nodes:
            messages_sent = node.send_hello_message(self, verbose=verbose)
            total_messages += messages_sent
            
        if verbose:
            print(f"Hello message exchange complete. {total_messages} messages exchanged.")
            
        return total_messages
    
    def propagate_topology_change(self, node_a_id, node_b_id, is_new_link=False, verbose=False):
        """Propagate information about a topology change throughout the network.
        
        Args:
            node_a_id, node_b_id: IDs of the nodes affected by the change
            is_new_link: Whether this is a new link (True) or a link failure (False)
            verbose: Whether to print detailed information
            
        Returns:
            Number of messages exchanged for topology propagation
        """
        node_a = self.get_node_by_id(node_a_id)
        node_b = self.get_node_by_id(node_b_id)
        
        if node_a is None or node_b is None:
            if verbose:
                print(f"Cannot propagate topology change - Node {node_a_id} or {node_b_id} not found")
            return 0
            
        messages = 0
        
        if is_new_link:
            # For a new link, nodes introduce themselves to each other
            if verbose:
                print(f"\nPropagating new link between Node {node_a_id} and Node {node_b_id}")
                
            if node_a.introduce_to_new_neighbor(node_b_id, self, verbose):
                messages += 1
                
            if node_b.introduce_to_new_neighbor(node_a_id, self, verbose):
                messages += 1
        else:
            # For a link failure, nodes notify their neighbors
            if verbose:
                print(f"\nPropagating link failure between Node {node_a_id} and Node {node_b_id}")
                
            node_a.notify_link_failure(node_b_id, self, verbose)
            node_b.notify_link_failure(node_a_id, self, verbose)
            
            # Count notifications to all neighbors of both nodes
            messages += len(node_a.get_neighbors()) + len(node_b.get_neighbors())
            
        if verbose:
            print(f"Topology change propagation complete. {messages} messages exchanged.")
            
        return messages
        
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
        
        # Record if this is a new link (wasn't previously connected)
        is_new_link = False
        if new_delay is not None and node_b_id not in node_a.connections:
            is_new_link = True
        
        # Update the connection
        if new_delay is None:
            # Remove the connection
            if node_b_id in node_a.connections:
                del node_a.connections[node_b_id]
                node_a.update_needed = True
            if node_a_id in node_b.connections:
                del node_b.connections[node_a_id]
                node_b.update_needed = True
                
            # Propagate link failure information
            self.propagate_topology_change(node_a_id, node_b_id, is_new_link=False, verbose=verbose)
        else:
            # Add or update the connection
            node_a.connections[node_b_id] = new_delay
            node_b.connections[node_a_id] = new_delay
            node_a.update_needed = True
            node_b.update_needed = True
            
            # Propagate new link information if this is a new link
            if is_new_link:
                self.propagate_topology_change(node_a_id, node_b_id, is_new_link=True, verbose=verbose)
            
        # Re-run the distance vector protocol to update routing tables
        return self.run_distance_vector_protocol(verbose=verbose)
