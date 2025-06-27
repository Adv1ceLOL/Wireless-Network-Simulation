from typing import List, Dict, Tuple, Optional, Set, Union
from src.core.sensor_node import SensorNode
import random
import time

class SensorNetwork:
    """A wireless sensor network consisting of nodes with weighted connections."""
    
    def __init__(self) -> None:
        """Initialize an empty sensor network."""
        self.nodes: List[SensorNode] = []
        
    def add_node(self, node: SensorNode) -> SensorNode:
        """Add a node to the network."""
        self.nodes.append(node)
        return node
        
    def create_random_network(self, n: int, area_size: Union[int, float] = 10, min_range: float = 1.0, max_range: float = 3.0) -> List[SensorNode]:
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
        SensorNode._all_nodes = []  # type: ignore
        
        for i in range(n):
            x: float = random.uniform(0, area_size)
            y: float = random.uniform(0, area_size)
            transmission_range: float = random.uniform(min_range, max_range)
            node: SensorNode = SensorNode(node_id=i, x=x, y=y, transmission_range=transmission_range)  # type: ignore
            self.nodes.append(node)
              # Generate weighted connections
        self._generate_connections()
        return self.nodes
        
    def _generate_connections(self, ensure_connected: bool = True) -> None:
        """Generate bidirectional weighted connections between nodes that can reach each other.
        
        Args:
            ensure_connected: If True, ensure no isolated nodes and a fully connected network
        """
        n: int = len(self.nodes)
        for i in range(n):
            for j in range(i + 1, n):
                node_a: SensorNode = self.nodes[i]
                node_b: SensorNode = self.nodes[j]
                if node_a.can_reach(node_b) or node_b.can_reach(node_a):  # type: ignore
                    delay: float = random.uniform(0, 1)
                    node_a.add_connection(node_b.node_id, delay)  # type: ignore
                    node_b.add_connection(node_a.node_id, delay)  # type: ignore
        
        if ensure_connected:
            # Ensure no isolated nodes (nodes without connections)
            self._ensure_no_isolated_nodes()
            
            # Ensure the network is fully connected (any node can reach any other)
            self._ensure_fully_connected_network()
                    
    def _ensure_no_isolated_nodes(self) -> None:
        """Ensure that every node has at least one connection."""
        isolated_nodes: List[SensorNode] = []
        
        # Find all isolated nodes
        for node in self.nodes:
            if len(node.connections) == 0:  # type: ignore
                isolated_nodes.append(node)
        
        if not isolated_nodes:
            return  # No isolated nodes, nothing to do
            
        print(f"Found {len(isolated_nodes)} isolated nodes, connecting them to the network...")
        
        # For each isolated node, find the closest non-isolated node and connect them
        for isolated_node in isolated_nodes:
            closest_node: Optional[SensorNode] = None
            min_distance: float = float('inf')
            
            # Find the closest non-isolated node
            for other_node in self.nodes:
                if other_node is isolated_node or other_node in isolated_nodes:
                    continue  # Skip self and other isolated nodes
                    
                distance: float = isolated_node.distance_to(other_node)  # type: ignore
                if distance < min_distance:
                    min_distance = distance
                    closest_node = other_node
            
            # If there are no non-isolated nodes (all nodes are isolated),
            # connect to another isolated node instead
            if closest_node is None and len(isolated_nodes) > 1:
                for other_node in isolated_nodes:
                    if other_node is isolated_node:
                        continue
                        
                    distance = isolated_node.distance_to(other_node)  # type: ignore
                    if distance < min_distance:
                        min_distance = distance
                        closest_node = other_node
            
            # If we found a node to connect to, create a bidirectional connection
            if closest_node is not None:
                # Increase the transmission range of both nodes to reach each other
                distance = isolated_node.distance_to(closest_node)  # type: ignore
                isolated_node.transmission_range = max(isolated_node.transmission_range, distance * 1.1)  # type: ignore
                closest_node.transmission_range = max(closest_node.transmission_range, distance * 1.1)  # type: ignore
                
                # Create the connection with a random delay
                delay: float = random.uniform(0, 1)
                isolated_node.add_connection(closest_node.node_id, delay)  # type: ignore
                closest_node.add_connection(isolated_node.node_id, delay)  # type: ignore
                
                print(f"Connected isolated Node {isolated_node.node_id} to Node {closest_node.node_id} (distance: {distance:.2f})")
            else:
                print(f"Warning: Could not find a suitable connection for Node {isolated_node.node_id}")
        
        # Recursively check again in case there are still isolated nodes
        # (This could happen in edge cases where all nodes were initially isolated)
        still_isolated: List[SensorNode] = [node for node in self.nodes if len(node.connections) == 0]  # type: ignore
        if still_isolated:
            print(f"There are still {len(still_isolated)} isolated nodes, attempting to connect them...")
            self._ensure_no_isolated_nodes()

    def _is_network_fully_connected(self) -> bool:
        """Check if the network is fully connected (any node can reach any other node).
        
        Returns:
            bool: True if the network is fully connected, False otherwise
        """
        if not self.nodes:
            return True  # Empty network is considered connected
            
        # Use breadth-first search to check connectivity
        n: int = len(self.nodes)
        visited: Set[int] = set()
        
        # Start BFS from the first node
        queue: List[int] = [0]  # Start with node 0
        visited.add(0)
        
        while queue:
            current: int = queue.pop(0)
            current_node: SensorNode = self.nodes[current]
            
            for neighbor_id in current_node.connections.keys():  # type: ignore
                if neighbor_id not in visited:
                    visited.add(neighbor_id)  # type: ignore
                    queue.append(neighbor_id)  # type: ignore
        
        # If all nodes are visited, the network is fully connected
        return len(visited) == n
        
    def _ensure_fully_connected_network(self) -> None:
        """Ensure the network is fully connected by identifying disconnected components
        and adding links between them.
        """
        if self._is_network_fully_connected():
            return  # Network is already fully connected
            
        print("Network is not fully connected. Identifying disconnected components...")
        
        # Identify all connected components using DFS
        n: int = len(self.nodes)
        components: List[Set[int]] = []
        visited: Set[int] = set()
        
        for i in range(n):
            if i in visited:
                continue
                
            # Find a new component
            component: Set[int] = set()
            stack: List[int] = [i]
            
            while stack:
                current: int = stack.pop()
                if current in component:
                    continue
                    
                component.add(current)
                visited.add(current)
                current_node: SensorNode = self.nodes[current]
                
                for neighbor_id in current_node.connections.keys():  # type: ignore
                    if neighbor_id not in component:
                        stack.append(neighbor_id)  # type: ignore
            
            components.append(component)
        
        print(f"Found {len(components)} disconnected components in the network")
        
        # Connect each component to the next one
        for i in range(len(components) - 1):
            # Find the closest pair of nodes between components i and i+1
            closest_pair: Optional[Tuple[int, int]] = None
            min_distance: float = float('inf')
            
            for node_id_1 in components[i]:
                for node_id_2 in components[i + 1]:
                    node_1: SensorNode = self.nodes[node_id_1]
                    node_2: SensorNode = self.nodes[node_id_2]
                    distance: float = node_1.distance_to(node_2)  # type: ignore
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_pair = (node_id_1, node_id_2)
            
            if closest_pair:
                node_1_id: int
                node_2_id: int
                node_1_id, node_2_id = closest_pair
                node_1 = self.nodes[node_1_id]
                node_2 = self.nodes[node_2_id]
                
                # Increase transmission range if needed
                distance = node_1.distance_to(node_2)  # type: ignore
                node_1.transmission_range = max(node_1.transmission_range, distance * 1.1)  # type: ignore
                node_2.transmission_range = max(node_2.transmission_range, distance * 1.1)  # type: ignore
                
                # Create a bidirectional connection
                delay: float = random.uniform(0, 1)
                node_1.add_connection(node_2_id, delay)  # type: ignore
                node_2.add_connection(node_1_id, delay)  # type: ignore
                
                print(f"Connected component {i} to component {i+1} by linking Node {node_1_id} to Node {node_2_id} (distance: {distance:.2f})")
        
        # Verify that the network is now fully connected
        if not self._is_network_fully_connected():
            print("Warning: Network is still not fully connected after attempting to connect components")
            # Try again with a more aggressive approach
            self._connect_all_components()
            
    def _connect_all_components(self) -> None:
        """A more aggressive approach to connect all components by connecting each
        component to all other components.
        """
        print("Using more aggressive approach to connect all components...")
        
        # Identify all connected components using DFS
        n: int = len(self.nodes)
        components: List[Set[int]] = []
        visited: Set[int] = set()  # type: ignore
        
        for i in range(n):
            if i in visited:
                continue
                
            # Find a new component
            component: Set[int] = set()  # type: ignore
            stack: List[int] = [i]
            
            while stack:
                current: int = stack.pop()
                if current in component:
                    continue
                    
                component.add(current)  # type: ignore
                visited.add(current)  # type: ignore
                current_node: SensorNode = self.nodes[current]
                
                for neighbor_id in current_node.connections.keys():  # type: ignore
                    if neighbor_id not in component:
                        stack.append(neighbor_id)  # type: ignore
            
            components.append(component)  # type: ignore
        
        # For each pair of components, connect the closest nodes
        for i in range(len(components)):  # type: ignore
            for j in range(i + 1, len(components)):  # type: ignore
                # Find the closest pair of nodes between components i and j
                closest_pair: Optional[Tuple[int, int]] = None
                min_distance: float = float('inf')
                
                for node_id_1 in components[i]:  # type: ignore
                    for node_id_2 in components[j]:  # type: ignore
                        node_1: SensorNode = self.nodes[node_id_1]  # type: ignore
                        node_2: SensorNode = self.nodes[node_id_2]  # type: ignore
                        distance: float = node_1.distance_to(node_2)  # type: ignore
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_pair = (node_id_1, node_id_2)  # type: ignore
                
                if closest_pair:
                    node_1_id: int
                    node_2_id: int  
                    node_1_id, node_2_id = closest_pair  # type: ignore
                    node_1 = self.nodes[node_1_id]
                    node_2 = self.nodes[node_2_id]
                    
                    # Increase transmission range if needed
                    distance = node_1.distance_to(node_2)  # type: ignore
                    node_1.transmission_range = max(node_1.transmission_range, distance * 1.1)  # type: ignore
                    node_2.transmission_range = max(node_2.transmission_range, distance * 1.1)  # type: ignore
                    
                    # Create a bidirectional connection
                    delay: float = random.uniform(0, 1)
                    node_1.add_connection(node_2_id, delay)  # type: ignore
                    node_2.add_connection(node_1_id, delay)  # type: ignore
                    
                    print(f"Connected component {i} to component {j} by linking Node {node_1_id} to Node {node_2_id} (distance: {distance:.2f})")
        
        # Final check
        if not self._is_network_fully_connected():
            print("Warning: Network is still not fully connected after aggressive connection attempt")
        else:
            print("Network is now fully connected")
                    
    def get_adjacency_matrix(self) -> List[List[float]]:
        """Return the adjacency matrix with delays as weights."""
        n: int = len(self.nodes)
        matrix: List[List[float]] = [[float('inf') for _ in range(n)] for _ in range(n)]
        
        # Fill in weights where connections exist
        for i, node in enumerate(self.nodes):
            matrix[i][i] = 0  # Set diagonal to 0
            for other_node_id, delay in node.connections.items():  # type: ignore
                matrix[i][other_node_id] = delay  # type: ignore
                
        return matrix
    
    def get_node_by_id(self, node_id: int) -> Optional[SensorNode]:
        """Return node with given ID."""
        for node in self.nodes:
            if node.node_id == node_id:  # type: ignore
                return node
        return None
    
    def get_all_links(self) -> List[Tuple[int, int, float]]:
        """Return a list of all links in the network as (node_a_id, node_b_id, delay) tuples."""
        links: List[Tuple[int, int, float]] = []
        for i, node in enumerate(self.nodes):
            for neighbor_id, delay in node.connections.items():  # type: ignore                # Only add each link once (when i < neighbor_id)
                if i < neighbor_id:  # type: ignore
                    links.append((i, neighbor_id, delay))  # type: ignore
        return links
    
    def get_message_counter_totals(self) -> Dict[str, int]:
        """Calculate total message counts across all nodes in the network.
        
        Returns:
            Dictionary with totals for each message type and a grand total
        """
        totals: Dict[str, int] = {
            "hello_msg_count": 0,
            "topology_msg_count": 0,
            "route_discovery_msg_count": 0,
            "data_packet_count": 0
        }
        
        for node in self.nodes:
            totals["hello_msg_count"] += node.hello_msg_count  # type: ignore
            totals["topology_msg_count"] += node.topology_msg_count  # type: ignore
            totals["route_discovery_msg_count"] += node.route_discovery_msg_count  # type: ignore
            totals["data_packet_count"] += node.data_packet_count  # type: ignore
            
        totals["total_messages"] = (totals["hello_msg_count"] + 
                                   totals["topology_msg_count"] + 
                                   totals["route_discovery_msg_count"] + 
                                   totals["data_packet_count"])
        
        return totals
    
    def simulate_message_transmission(self, source_id: int, target_id: int, message: str = "Test message", verbose: bool = True) -> Tuple[List[int], float, Optional[str]]:
        """Simulate sending a message from source to target using current routing tables.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            message: The message to send
            verbose: Whether to print status messages
            
        Returns:
            Tuple of (path, delay, error_reason)
            - path: List of node IDs in the transmission path, or empty list if no path
            - delay: Total transmission delay, or float('inf') if no path
            - error_reason: String describing the error if path is empty, otherwise None
        """
        if verbose:
            print(f"\nSimulating message transmission from Node {source_id} to Node {target_id}")
            print(f"Message: '{message}'")
        
        # Check if both nodes exist
        if source_id >= len(self.nodes) or source_id < 0:
            return [], float('inf'), f"Source node {source_id} does not exist"
        if target_id >= len(self.nodes) or target_id < 0:
            return [], float('inf'), f"Target node {target_id} does not exist"
        
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        
        # Check if target node is in source's routing table
        if target_id not in source_node.routing_table:
            return [], float('inf'), f"No route from node {source_id} to node {target_id} - nodes may be in different partitions"
            
        path: List[int] = []
        current: int = source_id
        
        try:
            while current != target_id:
                path.append(current)
                
                # Get next hop from routing table
                if target_id not in self.nodes[current].routing_table:
                    return [], float('inf'), f"Node {current} has no route to node {target_id} - network may be partitioned"
                
                next_hop, _ = self.nodes[current].routing_table.get(target_id, (None, float('inf')))
                
                if next_hop is None:
                    return [], float('inf'), f"No path found from node {current} to target - routing table incomplete"
                
                if next_hop in path:
                    return [], float('inf'), f"Routing loop detected at node {current} - invalid routing tables"
                
                # Increment data packet count for the forwarding node
                self.nodes[current].data_packet_count += 1
                current = next_hop
                
            path.append(target_id)
            total_delay: float = sum(self.nodes[path[i]].connections[path[i+1]] for i in range(len(path)-1))
            
            if verbose:
                print(f"Path found: {' -> '.join(map(str, path))}")
                print(f"Total transmission delay: {total_delay:.4f} units")
                
            return path, total_delay, None
            
        except (KeyError, IndexError) as e:
            # This can happen if a node or connection doesn't exist
            error_msg = f"Error while finding path: {str(e)}"
            if verbose:
                print(error_msg)
            return [], float('inf'), error_msg
    
    def run_distance_vector_protocol(self, max_iterations: int = 20, verbose: bool = False) -> int:
        """Run the proactive distance vector protocol until convergence or max iterations.
        
        Args:
            max_iterations: Maximum number of protocol iterations
            verbose: Print detailed information during protocol execution
        
        Returns:
            Number of iterations performed
        """
        # Initialize distance vectors for all nodes
        for node in self.nodes:
            node.initialize_distance_vector(self)  # type: ignore
            node.topology_msg_count += 1  # Count initial topology setup  # type: ignore
            
        if verbose:
            print("\nInitial distance vectors:")
            for node in self.nodes:
                print(f"Node {node.node_id}: {node.distance_vector}")  # type: ignore
        
        # Iteratively update distance vectors until convergence
        iteration: int = 0
        updates_occurred: bool = True
        
        while updates_occurred and iteration < max_iterations:
            iteration += 1
            if verbose:
                print(f"\nIteration {iteration}")
            
            # Phase 1: All nodes send their current distance vectors to neighbors
            updates_sent: bool = False
            for node in self.nodes:
                if node.send_distance_vector(self):  # type: ignore
                    updates_sent = True
                    
            # If no updates were sent, we're done
            if not updates_sent:
                if verbose:
                    print("No updates sent. Protocol has converged.")
                break
                
            # Phase 2: All nodes process received updates and update their routing tables
            updates_occurred = False
            for node in self.nodes:
                if node.update_routing_table():  # type: ignore
                    updates_occurred = True
                    if verbose:
                        print(f"Node {node.node_id} updated its routing table")  # type: ignore
            
            # Optional: Add a small delay to make the simulation more realistic
            time.sleep(0.01)
            
        if verbose:
            print(f"\nDistance vector protocol completed after {iteration} iterations")
            print("Final routing tables:")
            for node in self.nodes:
                node.print_routing_table()  # type: ignore
                
        return iteration
    
    def _find_shortest_path(self, source_id: int, target_id: int) -> Tuple[Optional[List[int]], float]:
        """Find shortest path between nodes using Dijkstra's algorithm."""
        n: int = len(self.nodes)
        distances: Dict[int, float] = {i: float('inf') for i in range(n)}
        distances[source_id] = 0
        predecessors: Dict[int, Optional[int]] = {i: None for i in range(n)}
        unvisited: Set[int] = set(range(n))
        
        while unvisited:
            current: int = min(unvisited, key=lambda x: distances[x])
            
            if current == target_id:
                # Reconstruct path
                path: List[int] = []
                current_node_id: Optional[int] = current
                while current_node_id is not None:
                    path.append(current_node_id)
                    current_node_id = predecessors[current_node_id]
                path.reverse()
                return path, distances[target_id]
                
            if distances[current] == float('inf'):
                break
                
            unvisited.remove(current)
            current_node: Optional[SensorNode] = self.get_node_by_id(current)
            
            if current_node is not None:
                for neighbor_id, delay in current_node.connections.items():  # type: ignore
                    if neighbor_id in unvisited:  # type: ignore
                        new_distance: float = distances[current] + delay  # type: ignore
                        if new_distance < distances[neighbor_id]:  # type: ignore
                            distances[neighbor_id] = new_distance  # type: ignore
                            predecessors[neighbor_id] = current  # type: ignore
        
        return None, float('inf')
    
    def handle_topology_change(self, node_a_id: int, node_b_id: int, new_delay: Optional[float] = None, 
                           verbose: bool = False, auto_reconnect: bool = True) -> int:
        """Handle a topology change (link addition, removal, or delay change).
        
        Args:
            node_a_id, node_b_id: IDs of the nodes affected by the change
            new_delay: New delay value, or None to remove the connection
            verbose: Print detailed information during update
            auto_reconnect: Whether to automatically reconnect isolated nodes
            
        Returns:
            Number of iterations to reconverge
        """
        node_a: Optional[SensorNode] = self.get_node_by_id(node_a_id)
        node_b: Optional[SensorNode] = self.get_node_by_id(node_b_id)
        
        if node_a is None or node_b is None:
            raise ValueError(f"Node with ID {node_a_id} or {node_b_id} not found")
            
        if verbose:
            if new_delay is None:
                print(f"\nRemoving connection between Node {node_a_id} and Node {node_b_id}")
            else:
                print(f"\nUpdating connection between Node {node_a_id} and Node {node_b_id} to delay {new_delay:.4f}")
        
        reconnection_info = None
        
        # Initialize reconnection info
        reconnection_info = {'isolated_nodes': [], 'reconnections': []}
        
        # Update the connection
        if new_delay is None:
            # Remove the connection
            if node_b_id in node_a.connections:  # type: ignore
                del node_a.connections[node_b_id]  # type: ignore
                node_a.update_needed = True  # type: ignore
            if node_a_id in node_b.connections:  # type: ignore
                del node_b.connections[node_a_id]  # type: ignore
                node_b.update_needed = True  # type: ignore
            
            # Check if either node becomes isolated (has no connections)
            isolated_nodes = []
            if len(node_a.connections) == 0:  # type: ignore
                isolated_nodes.append(node_a_id)
            if len(node_b.connections) == 0:  # type: ignore
                isolated_nodes.append(node_b_id)
                
            # Record isolated nodes without reconnecting them
            reconnection_info = {'isolated_nodes': isolated_nodes, 'reconnections': []}
        else:
            # Add or update the connection - validate transmission range first
            if not (node_a.can_reach(node_b) and node_b.can_reach(node_a)):  # type: ignore
                # Don't add the connection if nodes are out of range
                # Return 0 iterations since no change was made
                return 0
                
            node_a.connections[node_b_id] = new_delay  # type: ignore
            node_b.connections[node_a_id] = new_delay  # type: ignore
            node_a.update_needed = True  # type: ignore
            node_b.update_needed = True  # type: ignore
            
        # Re-run the distance vector protocol to update routing tables
        iterations = self.run_distance_vector_protocol(verbose=verbose)
        
        # Return both iterations and reconnection info
        if hasattr(self, '_last_reconnection_info'):
            self._last_reconnection_info = reconnection_info
        else:
            self._last_reconnection_info = reconnection_info
            
        return iterations
    
    def _reconnect_isolated_nodes(self, isolated_nodes: List[int], verbose: bool = False) -> Optional[Dict]:
        """Reconnect isolated nodes to the network.
        
        Args:
            isolated_nodes: List of node IDs that have become isolated
            verbose: Print detailed information
            
        Returns:
            Dictionary with reconnection information, or None if no reconnection needed
        """
        if not isolated_nodes:
            return None
            
        reconnections = []
        
        for isolated_node_id in isolated_nodes:
            if verbose:
                print(f"Node {isolated_node_id} is isolated, finding nearest node to reconnect...")
                
            isolated_node = self.get_node_by_id(isolated_node_id)
            if not isolated_node:
                continue
                
            # Find the nearest connected node
            min_distance = float('inf')
            best_target_id = None
            
            for potential_target in self.nodes:
                if potential_target.node_id == isolated_node_id:  # type: ignore
                    continue
                if len(potential_target.connections) == 0:  # type: ignore
                    continue  # Skip other isolated nodes
                    
                distance = isolated_node.distance_to(potential_target)  # type: ignore
                if distance < min_distance:
                    min_distance = distance
                    best_target_id = potential_target.node_id  # type: ignore
                    
            if best_target_id is not None:
                # Create reconnection
                delay = random.uniform(0.1, 1.0)
                target_node = self.get_node_by_id(best_target_id)
                
                if target_node:
                    isolated_node.add_connection(best_target_id, delay)  # type: ignore
                    target_node.add_connection(isolated_node_id, delay)  # type: ignore
                    
                    reconnections.append({
                        'isolated_node': isolated_node_id,
                        'connected_to': best_target_id,
                        'delay': delay,
                        'distance': min_distance
                    })
                    
                    if verbose:
                        print(f"Reconnected isolated Node {isolated_node_id} to Node {best_target_id} (distance: {min_distance:.2f}, delay: {delay:.3f})")
        
        return {'reconnections': reconnections} if reconnections else None
