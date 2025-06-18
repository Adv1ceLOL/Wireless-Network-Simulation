import os
from datetime import datetime
import numpy as np
import random

def generate_network_report(network, output_file=None):
    """
    Generate a detailed report of the network structure and save to a file.
    
    Args:
        network: A SensorNetwork instance
        output_file: Optional file path to save the report
    """
    # Create report string
    report = []
    
    # Header
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report.append('=' * 80)
    report.append(f"WIRELESS SENSOR NETWORK DETAILED REPORT - Generated: {timestamp}")
    report.append('=' * 80)
    
    # Network overview
    report.append(f"\n1. NETWORK OVERVIEW")
    report.append(f"-------------------")
    report.append(f"Number of nodes: {len(network.nodes)}")
    total_connections = sum(len(node.connections) for node in network.nodes)
    report.append(f"Total connections: {total_connections}")
    avg_connections = total_connections / len(network.nodes) if network.nodes else 0
    report.append(f"Average connections per node: {avg_connections:.2f}")
    
    # Calculate network density (actual connections / possible connections)
    max_possible = len(network.nodes) * (len(network.nodes) - 1)
    density = total_connections / max_possible if max_possible > 0 else 0
    report.append(f"Network density: {density:.4f} ({density*100:.1f}%)")
    
    # Node details
    report.append(f"\n2. NODE DETAILS")
    report.append(f"---------------")
    for i, node in enumerate(network.nodes):
        report.append(f"\n  Node {node.node_id}:")
        report.append(f"    Position: ({node.x:.4f}, {node.y:.4f})")
        report.append(f"    Transmission range: {node.transmission_range:.4f}")
        report.append(f"    Number of connections: {len(node.connections)}")
        
        if node.connections:
            report.append(f"    Connected to:")
            for neighbor_id, delay in sorted(node.connections.items()):
                neighbor = network.get_node_by_id(neighbor_id)
                distance = node.distance_to(neighbor)
                report.append(f"      → Node {neighbor_id}: delay={delay:.4f}, distance={distance:.4f}")
        
        # Show routing table for each node
        report.append(f"    Routing Table:")
        for dest, (next_hop, cost) in sorted(node.routing_table.items()):
            if next_hop is not None and cost < float('inf'):
                report.append(f"      Dest {dest}: Next hop {next_hop}, Cost {cost:.4f}")
            else:
                report.append(f"      Dest {dest}: unreachable")
    
    # Connection matrix
    report.append(f"\n3. ADJACENCY MATRIX (DELAY WEIGHTS)")
    report.append(f"-----------------------------------")
    matrix = network.get_adjacency_matrix()
    
    # Format matrix header
    header = "      " + "".join(f"{i:6d}" for i in range(len(network.nodes)))
    report.append(header)
    report.append("    " + "-" * (len(network.nodes) * 6 + 2))
    
    # Format matrix rows
    for i, row in enumerate(matrix):
        formatted_row = f"{i:4d} |"
        for value in row:
            if value == float('inf'):
                formatted_row += "     ∞"
            else:
                formatted_row += f"{value:6.3f}"
        report.append(formatted_row)
    
    # Network statistics
    report.append(f"\n4. NETWORK STATISTICS")
    report.append(f"---------------------")
    
    # Calculate average delay
    delays = [delay for node in network.nodes for delay in node.connections.values()]
    if delays:
        avg_delay = sum(delays) / len(delays)
        min_delay = min(delays)
        max_delay = max(delays)
        report.append(f"Delay statistics:")
        report.append(f"  - Minimum: {min_delay:.4f}")
        report.append(f"  - Maximum: {max_delay:.4f}")
        report.append(f"  - Average: {avg_delay:.4f}")
        report.append(f"  - Standard deviation: {np.std(delays):.4f}")
    
    # Path analysis
    report.append(f"\n5. PATH ANALYSIS")
    report.append(f"----------------")
    
    # Generate a connectivity map (which nodes can reach each other)
    report.append("Connectivity matrix (1=connected, 0=disconnected):")
    header = "      " + "".join(f"{i:4d}" for i in range(len(network.nodes)))
    report.append(header)
    report.append("    " + "-" * (len(network.nodes) * 4 + 2))
    
    # Check path existence between all node pairs
    for i in range(len(network.nodes)):
        row = f"{i:4d} |"
        for j in range(len(network.nodes)):
            if i == j:
                row += "   1"  # Self connection
            else:
                path, _ = network._find_shortest_path(i, j)
                row += "   1" if path else "   0"
        report.append(row)
    
    # Sample paths
    report.append("\nSample shortest paths between random node pairs:")
    
    # Choose 5 random paths to display (or fewer if network is small)
    n = len(network.nodes)
    samples = min(5, n*(n-1)//2)
    
    paths_shown = 0
    attempts = 0
    max_attempts = 20  # Prevent infinite loops in disconnected networks
    
    while paths_shown < samples and attempts < max_attempts:
        source = random.randint(0, n-1)
        target = random.randint(0, n-1)
        if source != target:
            path, delay = network._find_shortest_path(source, target)
            if path:
                report.append(f"  Path {source} → {target}:")
                report.append(f"    Nodes: {' → '.join(map(str, path))}")
                report.append(f"    Total delay: {delay:.4f}")
                report.append("")
                paths_shown += 1
        attempts += 1
    
    # Add simple connectivity graph visualization
    report.append(f"\n6. NETWORK CONNECTIVITY GRAPH")
    report.append(f"---------------------------")
    
    # Find fastest and most congested links
    if delays:
        max_delay_nodes = None
        min_delay_nodes = None
        
        for node in network.nodes:
            for neighbor_id, delay in node.connections.items():
                if delay == max_delay:
                    max_delay_nodes = (node.node_id, neighbor_id)
                if delay == min_delay:
                    min_delay_nodes = (node.node_id, neighbor_id)
        
        # Create a simple ASCII connectivity graph
        report.append("\nConnectivity visualization:")
        report.append("")
        report.append("Network topology:")
        report.append("")

        # Create a more visual network graph representation
        # First, create a node position mapping for ASCII art (2D grid positions)
        ascii_grid_size = 60  # Fixed width for clearer output
        ascii_grid_height = 25  # Fixed height for better proportions
        ascii_positions = {}
        
        # Map actual positions to grid positions proportionally
        max_x = max(node.x for node in network.nodes)
        max_y = max(node.y for node in network.nodes)
        min_x = min(node.x for node in network.nodes)
        min_y = min(node.y for node in network.nodes)
        
        # Add padding to prevent nodes at the edges
        pad_x = (max_x - min_x) * 0.1
        pad_y = (max_y - min_y) * 0.1
        
        # Adjust ranges to include padding
        range_x = max_x - min_x + 2 * pad_x
        range_y = max_y - min_y + 2 * pad_y
        min_x -= pad_x
        min_y -= pad_y
        
        # Create a node position dictionary with coordinates adjusted to grid size
        for node in network.nodes:
            # Scale the positions to fit in the grid with improved spacing
            grid_x = int(((node.x - min_x) / range_x) * (ascii_grid_size - 8)) + 4
            grid_y = int(((node.y - min_y) / range_y) * (ascii_grid_height - 6)) + 3
            ascii_positions[node.node_id] = (grid_x, grid_y)
        
        # Create the grid with improved dimensions
        grid = [[' ' for _ in range(ascii_grid_size)] for _ in range(ascii_grid_height)]
          # Add nodes to the grid
        for node_id, (x, y) in ascii_positions.items():
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                # Draw node bracket
                if x > 0:
                    grid[y][x-1] = '['
                if x + 1 < len(grid[0]):
                    grid[y][x+1] = ']'
                # Place node ID in the middle
                grid[y][x] = str(node_id) if node_id < 10 else str(node_id % 10)
          # Add edges to the grid using ASCII characters
        # Process connections to draw links
        connections_processed = set()
        for node in network.nodes:
            src_x, src_y = ascii_positions[node.node_id]
            for neighbor_id in node.get_neighbors():
                # Create a unique key for this connection to avoid duplicates
                conn_key = tuple(sorted([node.node_id, neighbor_id]))
                if conn_key in connections_processed:
                    continue
                connections_processed.add(conn_key)
                
                dst_x, dst_y = ascii_positions[neighbor_id]
                
                # Determine how to draw the connection
                dx = dst_x - src_x
                dy = dst_y - src_y
                
                # Handle horizontal connections
                if abs(dy) <= 1:  # Almost horizontal
                    for x in range(min(src_x, dst_x) + 2, max(src_x, dst_x) - 1):
                        if 0 <= src_y < len(grid) and 0 <= x < len(grid[0]):
                            grid[src_y][x] = '-'
                
                # Handle vertical connections
                elif abs(dx) <= 2:  # Almost vertical
                    for y in range(min(src_y, dst_y) + 1, max(src_y, dst_y)):
                        if 0 <= y < len(grid) and 0 <= src_x < len(grid[0]):
                            grid[y][src_x] = '|'
                
                # Handle diagonal connections
                else:
                    steps = max(abs(dx), abs(dy)) - 2  # Adjust for node brackets
                    if steps <= 0:
                        continue
                        
                    x_inc = (dx) / (steps + 1)  # +1 to avoid reaching exactly the node
                    y_inc = (dy) / (steps + 1)
                    
                    # Start from just outside the source node
                    curr_x = src_x + (2 if dx > 0 else -2)
                    curr_y = src_y
                    
                    for i in range(steps):
                        x = int(curr_x)
                        y = int(curr_y)
                        
                        if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] == ' ':
                            # Choose appropriate character for the connection
                            if abs(x_inc) >= 2 * abs(y_inc):
                                grid[y][x] = '-'
                            elif abs(y_inc) >= 2 * abs(x_inc):
                                grid[y][x] = '|'
                            elif (x_inc > 0 and y_inc > 0) or (x_inc < 0 and y_inc < 0):
                                grid[y][x] = '\\'
                            else:
                                grid[y][x] = '/'
                        
                        curr_x += x_inc
                        curr_y += y_inc
          # Convert grid to string and add to report
        for row in grid:
            # Only add non-empty lines with actual content
            line = ''.join(row).rstrip()
            if line.strip():
                report.append(line)
        
        report.append("")
        report.append("Legend: [N] = Node N, connections shown with -, |, \\, / characters")
        report.append("")
        
        report.append("")
        report.append(f"Most congested link: {max_delay_nodes[0]}-{max_delay_nodes[1]} (delay: {max_delay:.2f})")
        report.append(f"Fastest link: {min_delay_nodes[0]}-{min_delay_nodes[1]} (delay: {min_delay:.2f})")
    
    # Join report lines and print or save
    report_text = "\n".join(report)
    
    # Print to console
    print(report_text)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\nReport saved to {output_file}")
    
    return report_text
