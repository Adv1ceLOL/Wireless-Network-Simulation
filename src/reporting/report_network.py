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
    
    # Proactive Distance Vector Protocol information
    report.append(f"\n2. PROACTIVE DISTANCE VECTOR PROTOCOL")
    report.append(f"-------------------------------------")
    report.append(f"Protocol: Proactive Distance Vector Routing")
    report.append(f"Implementation: Distributed Bellman-Ford algorithm")
    report.append(f"Operation:")
    report.append(f"  - Nodes initialize with direct connections to neighbors")
    report.append(f"  - Nodes exchange distance vectors with neighbors")
    report.append(f"  - Nodes update routing tables based on received vectors")
    report.append(f"  - Process continues until no further updates are needed")
    report.append(f"Proactive Features:")
    report.append(f"  - Nodes maintain complete routing tables at all times")
    report.append(f"  - Topology changes trigger automatic routing updates")
    report.append(f"  - Routing tables converge to optimal paths")
    
    # Node details
    report.append(f"\n3. NODE DETAILS")
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
                report.append(f"      → Node {neighbor_id}: delay={delay:.4f}, distance={distance:.4f}")          # Show routing table and distance vector side by side in a more concise tabular format
        report.append(f"    Routing Table and Distance Vector:")
        # Create header rows for side-by-side tables
        report.append(f"      {'Dest':>4} | {'Next':>4} | {'Cost':>8}     {'Dest':>4} | {'Cost':>8}")
        report.append(f"      {'-'*4:>4}-|-{'-'*4:>4}-|-{'-'*8:>8}     {'-'*4:>4}-|-{'-'*8:>8}")
        
        # Get sorted items for both tables
        routing_items = sorted(node.routing_table.items())
        vector_items = sorted(node.distance_vector.items())
        max_items = max(len(routing_items), len(vector_items))
        
        # Create tabular data rows side by side
        for i in range(max_items):
            # Routing table row
            if i < len(routing_items):
                dest, (next_hop, cost) = routing_items[i]
                if next_hop is not None and cost < float('inf'):
                    routing_row = f"      {dest:4d} | {next_hop:4d} | {cost:8.4f}"
                else:
                    routing_row = f"      {dest:4d} | {'---':4} | {'∞':>8}"
            else:
                routing_row = f"      {'':4} | {'':4} | {'':8}"
                
            # Distance vector row
            if i < len(vector_items):
                dest, cost = vector_items[i]
                if cost < float('inf'):
                    vector_row = f"     {dest:4d} | {cost:8.4f}"
                else:
                    vector_row = f"     {dest:4d} | {'∞':>8}"
            else:
                vector_row = f"     {'':4} | {'':8}"
                
            # Combine rows
            report.append(f"{routing_row}{vector_row}")
    
    # Connection matrix
    report.append(f"\n4. ADJACENCY MATRIX (DELAY WEIGHTS)")
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
    report.append(f"\n5. NETWORK STATISTICS")
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
    
    # Routing metrics
    unreachable = 0
    total_paths = 0
    total_hops = 0
    total_path_cost = 0
    
    for node in network.nodes:
        for dest_id, (next_hop, cost) in node.routing_table.items():
            if node.node_id != dest_id:  # Skip self-routes
                total_paths += 1
                if next_hop is None or cost == float('inf'):
                    unreachable += 1
                else:
                    # Count hops in the path
                    hops = 0
                    current = node.node_id
                    while current != dest_id:
                        hops += 1
                        current = network.nodes[current].routing_table[dest_id][0]
                        # Prevent infinite loops
                        if hops > len(network.nodes):
                            break
                    total_hops += hops
                    total_path_cost += cost
    
    if total_paths > 0:
        reachability = (total_paths - unreachable) / total_paths
        report.append(f"\nRouting metrics:")
        report.append(f"  - Reachability: {reachability:.4f} ({reachability*100:.1f}%)")
        report.append(f"  - Unreachable destinations: {unreachable}")
        
        if total_paths > unreachable:
            avg_hops = total_hops / (total_paths - unreachable)
            avg_cost = total_path_cost / (total_paths - unreachable)
            report.append(f"  - Average hops per path: {avg_hops:.2f}")
            report.append(f"  - Average path cost: {avg_cost:.4f}")
      # Sample paths
    report.append(f"\n6. SAMPLE PATHS")
    report.append(f"----------------")
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
      # Network link information
    report.append(f"\n7. NETWORK LINK INFORMATION")
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
