"""
Protocol Evaluation Module

This module provides functions for evaluating the protocol efficiency under different
network conditions and parameters.
"""

from src.core.network import SensorNetwork
from src.visualization.visualization import visualize_adjacency_list
from src.core.evaluation_score import calculate_topology_score
import random
import os
import math

def get_protocol_efficiency(network):
    """Calculate protocol efficiency as data packets / total packets.
    
    Args:
        network: The SensorNetwork instance to evaluate
        
    Returns:
        Float representing efficiency (data packets / total packets)
    """
    # Calculate data packets and total messages
    data_packets = 0
    hello_msgs = 0
    topology_msgs = 0
    route_discovery_msgs = 0
    
    for node in network.nodes:
        data_packets += getattr(node, 'data_packet_count', 0)
        hello_msgs += getattr(node, 'hello_msg_count', 0)
        topology_msgs += getattr(node, 'topology_msg_count', 0)
        route_discovery_msgs += getattr(node, 'route_discovery_msg_count', 0)
    
    total_packets = hello_msgs + topology_msgs + route_discovery_msgs + data_packets
    
    if total_packets == 0:
        return 0.0
        
    return data_packets / total_packets

def run_evaluation_scenario(network, time_steps=5, p_request=0.3, p_fail=0.1, p_new=0.1, verbose=False):
    """Run a single evaluation scenario with the given parameters.
    
    Args:
        network: The SensorNetwork instance to evaluate
        time_steps: Number of time steps to simulate
        p_request: Probability of a packet request
        p_fail: Probability of a link failure
        p_new: Probability of a new link
        verbose: Whether to print detailed information
        
    Returns:
        Dictionary with evaluation statistics
    """
    # Reset message counters
    for node in network.nodes:
        node.hello_msg_count = 0
        node.topology_msg_count = 0
        node.route_discovery_msg_count = 0
        node.data_packet_count = 0
        
    # Statistics tracking
    stats = {
        "requests": 0,
        "successful_transmissions": 0,
        "failed_transmissions": 0,
        "links_removed": 0,
        "links_added": 0,
        "reconnections_needed": 0,
        "total_delay": 0,
        "total_hops": 0,
        "reconvergence_iterations": 0,
        "sent_messages": 0
    }
    
    n_nodes = len(network.nodes)
    
    # Run the protocol initially to ensure routing tables are built
    initial_iterations = network.run_distance_vector_protocol(verbose=False)
    
    # Save original network connectivity state
    original_links = network.get_all_links()
    
    # Apply topology changes (link failure or addition) - only once per iteration
    
    # 1. Randomly remove links with probability p_fail (max one per iteration)
    if random.random() < p_fail and len(network.get_all_links()) > 0:
        # Select a random existing link
        links = network.get_all_links()
        if links:
            node_a_id, node_b_id, _ = random.choice(links)
            # Note: handle_topology_change may reconnect the network if it becomes disconnected
            iterations = network.handle_topology_change(node_a_id, node_b_id, new_delay=None, verbose=False)
            stats["links_removed"] += 1
            stats["reconvergence_iterations"] += iterations
            
            # Check if the network needed reconnection (this indicates handle_topology_change had to fix connectivity)
            new_links = network.get_all_links()
            if len(new_links) >= len(links):  # If we didn't actually lose a link (it was reconnected)
                stats["reconnections_needed"] += 1
    
    # 2. Randomly add new links with probability p_new (max one per iteration)
    if random.random() < p_new:
        # Find nodes that aren't connected
        unconnected_pairs = []
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if j not in network.nodes[i].connections:
                    # Check if they're mutually within range
                    node_a = network.nodes[i]
                    node_b = network.nodes[j]
                    if node_a.can_reach(node_b) and node_b.can_reach(node_a):
                        unconnected_pairs.append((i, j))
        if unconnected_pairs:                
            node_a_id, node_b_id = random.choice(unconnected_pairs)
            delay = random.uniform(0.1, 1.0)
            iterations = network.handle_topology_change(node_a_id, node_b_id, new_delay=delay, verbose=False)
            stats["links_added"] += 1
            stats["reconvergence_iterations"] += iterations
    
    # Now simulate time steps (hello messages + packet requests per time step)
    for t in range(time_steps):
        # 1. Hello message exchange 
        for node in network.nodes:
            # Each node sends one hello message to each of its neighbors
            hello_msgs = len(node.connections)
            node.hello_msg_count += hello_msgs
        
        # 2. Process random packet request with probability p_request (max one per time step)
        if random.random() < p_request:
            source_id = random.randint(0, n_nodes-1)
            dest_id = random.randint(0, n_nodes-1)
            while dest_id == source_id:
                dest_id = random.randint(0, n_nodes-1)
            message = f"Packet request at t={t+1}"
            
            path, delay, error = network.simulate_message_transmission(source_id, dest_id, message, verbose=False)
            stats["requests"] += 1
            if path:
                stats["successful_transmissions"] += 1
                stats["total_delay"] += delay
                # Track path length (number of hops) for routing distance calculations
                if path:
                    hop_count = len(path) - 1  # Number of hops is path length - 1
                    stats["total_hops"] = stats.get("total_hops", 0) + hop_count
            else:
                stats["failed_transmissions"] += 1
    # Calculate efficiency metrics
    data_packets = 0
    hello_msgs = 0
    topology_msgs = 0
    route_discovery_msgs = 0
    
    for node in network.nodes:
        data_packets += getattr(node, 'data_packet_count', 0)
        hello_msgs += getattr(node, 'hello_msg_count', 0)
        topology_msgs += getattr(node, 'topology_msg_count', 0)
        route_discovery_msgs += getattr(node, 'route_discovery_msg_count', 0)
    
    total_packets = hello_msgs + topology_msgs + route_discovery_msgs + data_packets
    efficiency = get_protocol_efficiency(network)
    stats.update({
        "data_packets": data_packets,
        "hello_msgs": hello_msgs,
        "topology_msgs": topology_msgs,
        "route_discovery_msgs": route_discovery_msgs,
        "total_packets": total_packets,
        "sent_messages": data_packets,  # Changed to only count data packets
        "efficiency": efficiency,
        "p_request": p_request,
        "p_fail": p_fail,
        "p_new": p_new
    })
    
    return stats

def run_evaluation(n_topologies=1, iterations_per_topology=100, max_probability=0.3, n_nodes=20, area_size=10, fixed_p_request=0.5, fixed_p_fail=None, fixed_p_new=None, time_steps=5):
    """Run a comprehensive evaluation of the protocol with varying parameters.
    
    Args:
        n_topologies: Number of random network topologies to evaluate
        iterations_per_topology: Number of iterations with different parameters per topology
        max_probability: Maximum value for random probability parameters (p_fail, p_new)
        n_nodes: Number of nodes in each topology
        area_size: Size of the simulation area
        fixed_p_request: Fixed probability for packet requests (if None, uses random values)
        fixed_p_fail: Fixed probability for link failures (if None, uses random values)
        fixed_p_new: Fixed probability for new links (if None, uses random values)  
        time_steps: Number of time steps to simulate per iteration
        
    Returns:
        Dictionary with evaluation statistics
    """
    print(f"\n{'='*70}")
    print(f"PROTOCOL EVALUATION MODE")
    print(f"Topologies: {n_topologies}, Iterations per topology: {iterations_per_topology}")
    print(f"Maximum probability value for dynamic parameters: {max_probability}")
    print(f"Fixed p_request value: {fixed_p_request}")
    if fixed_p_fail is not None:
        print(f"Fixed p_fail value: {fixed_p_fail}")
    else:
        print(f"Random p_fail values: 0.01 to {max_probability}")
    if fixed_p_new is not None:
        print(f"Fixed p_new value: {fixed_p_new}")
    else:
        print(f"Random p_new values: 0.01 to {max_probability}")
    print(f"{'='*70}\n")
    
    # Store results for final report
    evaluation_results = []
    
    # For each topology
    for topo_idx in range(n_topologies):
        print(f"\n{'-'*70}")
        print(f"EVALUATING TOPOLOGY {topo_idx+1}/{n_topologies}")
        print(f"{'-'*70}")
        
        # Create a new random network
        network = SensorNetwork()
        network.create_random_network(n_nodes, area_size)
        
        # Display adjacency list for this topology
        print("\nTopology Adjacency List:")
        visualize_adjacency_list(network, interactive=False)
        
        # Initial protocol convergence
        print("\nRunning initial protocol convergence...")
        iterations = network.run_distance_vector_protocol(verbose=False)
        print(f"Initial protocol convergence: {iterations} iterations")
        
        # Store results for this topology
        topology_results = []
        
        # Run iterations with different parameters
        for iter_idx in range(iterations_per_topology):
            # Use fixed values if provided, otherwise use random values
            p_request = fixed_p_request  # Always use fixed value for p_request
            
            if fixed_p_fail is not None:
                p_fail = fixed_p_fail  # Use fixed value
            else:
                p_fail = random.uniform(0.01, max_probability)  # Use random value
                
            if fixed_p_new is not None:
                p_new = fixed_p_new  # Use fixed value
            else:
                p_new = random.uniform(0.01, max_probability)  # Use random value
            
            # Determine parameter status for display
            p_fail_status = "fixed" if fixed_p_fail is not None else "random"
            p_new_status = "fixed" if fixed_p_new is not None else "random"
            
            # Run one simulation step with the parameters
            print(f"\nIteration {iter_idx+1}/{iterations_per_topology}: p_request={p_request:.3f} (fixed), p_fail={p_fail:.3f} ({p_fail_status}), p_new={p_new:.3f} ({p_new_status})")
            
            # Run a mini evaluation scenario with these parameters
            stats = run_evaluation_scenario(
                network, 
                time_steps=time_steps, 
                p_request=p_request, 
                p_fail=p_fail, 
                p_new=p_new, 
                verbose=False
            )
              # Print key statistics
            efficiency = stats["efficiency"]
            data_packets = stats["data_packets"]
            total_packets = stats["total_packets"]
            reconnections = stats["reconnections_needed"]
            links_removed = stats["links_removed"]
            links_added = stats["links_added"]
            
            print(f"Efficiency: {efficiency:.4f} (Data packets: {data_packets}, Total packets: {total_packets})")
            print(f"Links removed: {links_removed}, Links added: {links_added}")
            if reconnections > 0:
                print(f"Note: Network needed reconnection {reconnections} times due to disconnected components")            # Store results for this iteration
            iteration_result = {
                "topology": topo_idx + 1,
                "iteration": iter_idx + 1,
                "p_request": p_request,
                "p_fail": p_fail,
                "p_new": p_new,
                "data_packets": data_packets,
                "total_packets": total_packets,
                "efficiency": efficiency,
                "reconnections": reconnections,
                "links_removed": links_removed,
                "links_added": links_added,
                "sent_messages": data_packets,  # Changed to only count data packets
                "total_hops": stats.get("total_hops", 0),
                "total_delay": stats.get("total_delay", 0)
            }
            topology_results.append(iteration_result)
            evaluation_results.append(iteration_result)
    
    # Generate final report
    print(f"\n{'='*70}")
    print("FINAL EVALUATION REPORT")
    print(f"{'='*70}")    # Calculate averages per topology
    topology_summaries = []
    for topo_idx in range(n_topologies):
        topo_results = [r for r in evaluation_results if r["topology"] == topo_idx + 1]
        if topo_results:
            # Calculate average values
            avg_efficiency = sum(r["efficiency"] for r in topo_results) / len(topo_results)
            avg_p_request = sum(r["p_request"] for r in topo_results) / len(topo_results)
            avg_p_fail = sum(r["p_fail"] for r in topo_results) / len(topo_results)
            avg_p_new = sum(r["p_new"] for r in topo_results) / len(topo_results)
            avg_reconnections = sum(r["reconnections"] for r in topo_results) / len(topo_results)
              # Sum up total values
            total_data_packets = sum(r["data_packets"] for r in topo_results)
            total_msg_packets = sum(r["total_packets"] for r in topo_results)
            total_links_removed = sum(r["links_removed"] for r in topo_results)
            total_links_added = sum(r["links_added"] for r in topo_results)
            total_sent_messages = sum(r["sent_messages"] for r in topo_results)
            total_hops = sum(r["total_hops"] for r in topo_results)
            total_delay = sum(r["total_delay"] for r in topo_results)
            
            # Calculate routing efficiency metrics
            successful_transmissions = sum(r["data_packets"] for r in topo_results)
            avg_hops_per_message = total_hops / max(1, successful_transmissions)
            avg_delay_per_message = total_delay / max(1, successful_transmissions)
            
            topology_summaries.append({
                "topology": topo_idx + 1,
                "avg_efficiency": avg_efficiency,
                "avg_p_request": avg_p_request,
                "avg_p_fail": avg_p_fail,
                "avg_p_new": avg_p_new,
                "avg_reconnections": avg_reconnections,
                "total_data_packets": total_data_packets,
                "total_msg_packets": total_msg_packets,
                "total_links_removed": total_links_removed,
                "total_links_added": total_links_added,
                "total_sent_messages": total_sent_messages,
                "total_hops": total_hops,
                "total_delay": total_delay,
                "avg_hops_per_message": avg_hops_per_message,
                "avg_delay_per_message": avg_delay_per_message
            })
      # Print summary table - TRANSPOSED format (topology as columns, metrics as rows)
    print("\nProtocol Evaluation Summary (Transposed):")
    
    # Print header row with topology numbers
    header = "Metric"
    for summary in topology_summaries:
        header += f" | Topology {summary['topology']}"
    print(header)
    print("-" * len(header))      # Print metrics as rows
    metrics = [
        ("Mean Efficiency", "avg_efficiency", "{:.4f}"),
        ("Mean p_request", "avg_p_request", "{:.4f}"),
        ("Mean p_fail", "avg_p_fail", "{:.4f}"),
        ("Mean p_new", "avg_p_new", "{:.4f}"),
        ("Mean Reconnections", "avg_reconnections", "{:.2f}"),
        ("Links Removed", "total_links_removed", "{}"),
        ("Links Added", "total_links_added", "{}"),
        ("Total Data Messages", "total_sent_messages", "{}"),
        ("Avg Hops/Message", "avg_hops_per_message", "{:.2f}"),
        ("Avg Delay/Message", "avg_delay_per_message", "{:.4f}")
    ]
    
    for metric_name, metric_key, format_str in metrics:
        row = f"{metric_name:<20}"
        for summary in topology_summaries:
            value = summary[metric_key]
            formatted_value = format_str.format(value)
            row += f" | {formatted_value:>12}"
        print(row)
      # Calculate overall average
    overall_avg_efficiency = sum(s["avg_efficiency"] for s in topology_summaries) / len(topology_summaries)
    print(f"\nOverall average efficiency: {overall_avg_efficiency:.4f}")      # Compare and rank topologies
    if len(topology_summaries) > 1:
        print("\nTopology Ranking (higher score is better):")
        rankings = compare_topologies(topology_summaries)
        for ranking in rankings:
            print(f"Rank {ranking['rank']}: Topology {ranking['topology']} - Score: {ranking['score']:.4f}")
        
        # Identify the best topology
        best_topology = rankings[0]
        print(f"\nBest topology: Topology {best_topology['topology']} with score {best_topology['score']:.4f}")
        
        # Display detailed scoring components for the best topology        print(f"\nDetailed Scoring Components for Best Topology:")
        detailed = best_topology["detailed_scores"]
        print(f"  - Efficiency:        {detailed['efficiency']:.4f} (weight: 0.25)")
        print(f"  - Resilience:        {detailed['resilience']:.4f} (weight: 0.20)")
        print(f"  - Overhead:          {detailed['overhead']:.4f} (weight: 0.15)")
        print(f"  - Routing Quality:   {detailed['routing_quality']:.4f} (weight: 0.20)")
        print(f"  - Delay Factor:      {detailed['delay_factor']:.4f} (weight: 0.10)")
        print(f"  - Traffic Balance:   {detailed['traffic_balance']:.4f} (weight: 0.10)")
        
        # Display additional metrics about the best topology
        print(f"\nAdditional Network Metrics for Best Topology:")
        print(f"  - Link Stability:      {best_topology['link_stability']:.4f} (ratio of stable links)")
        print(f"  - Messages per Link:   {best_topology['messages_per_link']:.2f} (data msgs per link event)")
        print(f"  - Network Efficiency:  {best_topology['avg_efficiency']:.4f} (data/total msgs ratio)")
        print(f"  - Link Changes:        {best_topology['total_links_removed'] + best_topology['total_links_added']} (total topology changes)")
      # Generate detailed report file
    report_dir = os.path.join("output", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, "evaluation_report.txt")
    
    with open(report_file, "w") as f:
        f.write(f"PROTOCOL EVALUATION REPORT\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Evaluation Parameters:\n")
        f.write(f"  Number of topologies: {n_topologies}\n")
        f.write(f"  Iterations per topology: {iterations_per_topology}\n")
        f.write(f"  Maximum probability value: {max_probability}\n")        
        f.write(f"  Fixed p_request value: {fixed_p_request}\n")
        f.write(f"  Nodes per topology: {n_nodes}\n\n")
        
        f.write("Detailed Results:\n")
        f.write(f"{'Topology':<10} {'Iteration':<10} {'p_request':<10} {'p_fail':<10} {'p_new':<10} {'Efficiency':<10} {'Links Removed':<15} {'Links Added':<15} {'Data Messages':<15} {'Reconnects':<10}\n")
        f.write("-" * 120 + "\n")
        
        for result in evaluation_results:
            f.write(f"{result['topology']:<10} {result['iteration']:<10} {result['p_request']:<10.3f} "
                    f"{result['p_fail']:<10.3f} {result['p_new']:<10.3f} {result['efficiency']:<10.4f} "
                    f"{result['links_removed']:<15} {result['links_added']:<15} {result['sent_messages']:<15} "
                    f"{result['reconnections']:<10}\n")
        
        # Write transposed summary table
        f.write("\nSUMMARY TABLE (TRANSPOSED - TOPOLOGY AS COLUMNS):\n")
        f.write("-" * 70 + "\n")
        
        # Write header row with topology numbers
        header = "Metric"
        for summary in topology_summaries:
            header += f" | Topology {summary['topology']}"
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")          # Write metrics as rows
        metrics = [
            ("Mean Efficiency", "avg_efficiency", "{:.4f}"),
            ("Mean p_request", "avg_p_request", "{:.4f}"),
            ("Mean p_fail", "avg_p_fail", "{:.4f}"),
            ("Mean p_new", "avg_p_new", "{:.4f}"),
            ("Mean Reconnections", "avg_reconnections", "{:.2f}"),
            ("Links Removed", "total_links_removed", "{}"),
            ("Links Added", "total_links_added", "{}"),
            ("Total Data Messages", "total_sent_messages", "{}"),
            ("Avg Hops/Message", "avg_hops_per_message", "{:.2f}"),
            ("Avg Delay/Message", "avg_delay_per_message", "{:.4f}")
        ]
        
        for metric_name, metric_key, format_str in metrics:
            row = f"{metric_name:<20}"
            for summary in topology_summaries:
                value = summary[metric_key]
                formatted_value = format_str.format(value)
                row += f" | {formatted_value:>12}"
            f.write(row + "\n")
        f.write(f"\nOverall average efficiency: {overall_avg_efficiency:.4f}\n")        # Add topology ranking to report
        if len(topology_summaries) > 1:
            f.write("\nTOPOLOGY RANKING (higher score is better):\n")
            f.write("-" * 70 + "\n")
            
            rankings = compare_topologies(topology_summaries)
            for ranking in rankings:
                f.write(f"Rank {ranking['rank']}: Topology {ranking['topology']} - Score: {ranking['score']:.4f}\n")
              # Identify the best topology
            best_topology = rankings[0]            
            f.write(f"\nBest topology: Topology {best_topology['topology']} with score {best_topology['score']:.4f}\n")
            
            # Add explanation of the enhanced scoring formula
            f.write("\nComprehensive Scoring Formula:\n")
            f.write("  Score = (0.25 * Efficiency) + (0.20 * Resilience) + (0.15 * Overhead) + \n")
            f.write("          (0.20 * Routing Quality) + (0.10 * Delay Factor) + (0.10 * Traffic Balance)\n")
            f.write("  where:\n")
            f.write("  - Efficiency: Ratio of data packets to total packets\n")
            f.write("  - Resilience: Network ability to handle topology changes and maintain connectivity\n")
            f.write("  - Overhead: Efficiency of control message usage\n")
            f.write("  - Routing Quality: Quality of routing paths based on average hop count (fewer is better)\n")            
            f.write("  - Delay Factor: Quality of paths based on link weights/delays (lower is better)\n")
            f.write("  - Traffic Balance: Balance between data volume and network capacity\n")
            
            # Add detailed scores for best topology
            f.write("\nDetailed Scoring Components for Best Topology:\n")
            detailed = best_topology["detailed_scores"]
            f.write(f"  - Efficiency:        {detailed['efficiency']:.4f} (weight: 0.25)\n")
            f.write(f"  - Resilience:        {detailed['resilience']:.4f} (weight: 0.20)\n")
            f.write(f"  - Overhead:          {detailed['overhead']:.4f} (weight: 0.15)\n")
            f.write(f"  - Routing Quality:   {detailed['routing_quality']:.4f} (weight: 0.20)\n")
            f.write(f"  - Delay Factor:      {detailed['delay_factor']:.4f} (weight: 0.10)\n")
            f.write(f"  - Traffic Balance:   {detailed['traffic_balance']:.4f} (weight: 0.10)\n")
            
            # Add additional network metrics for best topology
            f.write("\nAdditional Network Metrics for Best Topology:\n")
            f.write(f"  - Link Stability:      {best_topology['link_stability']:.4f} (ratio of stable links)\n")
            f.write(f"  - Messages per Link:   {best_topology['messages_per_link']:.2f} (data msgs per link event)\n")
            f.write(f"  - Network Efficiency:  {best_topology['avg_efficiency']:.4f} (data/total msgs ratio)\n")
            f.write(f"  - Link Changes:        {best_topology['total_links_removed'] + best_topology['total_links_added']} (total topology changes)\n")
            
            # Add cross-topology comparison
            f.write("\nCross-Topology Metric Comparison:\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Metric':<20} {'Best Value':<12} {'Worst Value':<12} {'Range':<12} {'Topology ID':<12}\n")
            
            # Compare metrics across topologies
            metrics_to_compare = [
                ("Efficiency", "avg_efficiency", True),  # True = higher is better
                ("Link Stability", "link_stability", True),
                ("Messages/Link", "messages_per_link", True),
                ("Reconnections", "avg_reconnections", False)  # False = lower is better
            ]
            
            for metric_name, metric_key, higher_is_better in metrics_to_compare:
                if metric_key == "link_stability" or metric_key == "messages_per_link":
                    values = [(r[metric_key], r["topology"]) for r in rankings]
                else:
                    values = [(r[metric_key] if metric_key in r else r.get("detailed_scores", {}).get(metric_key, 0), 
                              r["topology"]) for r in rankings]
                
                if higher_is_better:
                    best = max(values, key=lambda x: x[0])
                    worst = min(values, key=lambda x: x[0])
                else:
                    best = min(values, key=lambda x: x[0])
                    worst = max(values, key=lambda x: x[0])
                
                value_range = abs(best[0] - worst[0])
                f.write(f"{metric_name:<20} {best[0]:<12.4f} {worst[0]:<12.4f} {value_range:<12.4f} {best[1]:<12}\n")
        
        f.write("\nNote on network reconnections:\n")
        f.write("  The 'Reconnects' column shows how many times the network needed to be\n")
        f.write("  reconnected after a link failure caused disconnected components.\n")        
        f.write("  This is an important resilience feature of the protocol.\n")
        
        f.write("\nNote on statistics:\n")
        f.write("  - Links Removed/Added: The total number of links that were removed/added during evaluation\n")
        f.write("  - Total Data Messages: The total number of data packets transmitted (excluding control messages)\n")
        f.write("  - Mean Efficiency: The ratio of data packets to total packets (higher is better)\n")
    
    print(f"\nDetailed evaluation report saved to: {report_file}")
    
    return {"overall_efficiency": overall_avg_efficiency, "topology_summaries": topology_summaries}

def calculate_topology_score(topology_summary, weights=None):
    """Calculate a comprehensive score for a topology based on multiple network performance metrics.
    
    The score is calculated as a weighted combination of:
    - Efficiency: Ratio of data packets to total packets
    - Resilience: Based on network's ability to handle topology changes
    - Overhead: Control message efficiency
    - Routing Quality: Optimality of routing paths (based on hops)
    - Delay Factor: Quality of paths based on link weights/delays
    - Traffic Balance: Balance between data volume and network capacity
    
    Args:
        topology_summary: Dictionary with topology summary metrics
        weights: Optional dictionary with custom weights for each component
        
    Returns:
        Float representing the overall topology score (higher is better)
    """
    # Default weights if not provided
    if weights is None:
        weights = {
            "efficiency": 0.25,    # Protocol efficiency
            "resilience": 0.20,    # Network resilience to failures
            "overhead": 0.15,      # Control message overhead
            "routing_quality": 0.20,  # Quality of routing paths (hops)
            "delay_factor": 0.10,   # Quality of paths based on link weights/delays
            "traffic_balance": 0.10   # Balance of traffic across network
        }
    
    # 1. Basic Efficiency - ratio of data packets to total packets
    efficiency = topology_summary["avg_efficiency"]
    
    # 2. Resilience - ability to maintain connectivity despite failures
    reconnections = topology_summary["avg_reconnections"]
    links_removed = topology_summary["total_links_removed"]
    # More sophisticated resilience formula that gives diminishing penalties
    # for increasing failures, using a logarithmic scale
    resilience_base = max(0.1, 1.0 - (reconnections/5.0)) # Base resilience from reconnections
    link_failure_impact = max(0.1, 1.0 - (math.log(links_removed + 1) / 10.0)) # Impact of link failures
    resilience_factor = (resilience_base + link_failure_impact) / 2.0
    
    # 3. Overhead - control message efficiency
    data_messages = topology_summary["total_sent_messages"]
    # Avoid division by zero
    if data_messages == 0:
        overhead_factor = 0
    else:
        # Calculate ratio of control messages to data messages
        control_messages = topology_summary["total_msg_packets"] - data_messages
        # Normalize overhead based on network size (assuming average network has ~15 nodes)
        overhead_ratio = control_messages / max(1, data_messages)
        overhead_factor = 1.0 / (1.0 + (overhead_ratio / 3.0))  # Scale to reasonable range
    
    # 4. Routing Quality - based on average hops per message
    # Lower hops means better routing paths
    avg_hops = topology_summary.get("avg_hops_per_message", 0)
    successful_transmissions = topology_summary["total_sent_messages"]
    
    if successful_transmissions == 0 or avg_hops == 0:
        routing_quality = 0  # No successful transmissions or hop data
    else:
        # Better score for fewer hops - assume 15 nodes max (n_nodes) so worst case is n-1 hops
        # Inverse relationship - fewer hops is better
        routing_quality = max(0.1, 1.0 - (avg_hops / 14.0))
    
    # 5. Delay Factor - quality of paths based on link weights/delays
    avg_delay = topology_summary.get("avg_delay_per_message", 0)
    
    if successful_transmissions == 0 or avg_delay == 0:
        delay_factor = 0  # No successful transmissions or delay data
    else:
        # Normalize delay to 0-1 range (assuming reasonable delay is < 5.0)
        # Inverse relationship - lower delay is better
        delay_factor = max(0.1, 1.0 - (avg_delay / 5.0))
    
    # 6. Traffic Balance - balance between data volume and protocol overhead
    # Ideally, as data volume increases, protocol overhead should decrease relatively
    if data_messages > 0:
        # Ratio of data messages to total messages - higher is better
        traffic_ratio = data_messages / topology_summary["total_msg_packets"]
        # Normalize using sigmoid function to get smooth 0-1 range
        traffic_balance = 1.0 / (1.0 + math.exp(-10 * (traffic_ratio - 0.1)))
    else:
        traffic_balance = 0
      # Calculate composite score (higher is better)
    score = (
        weights["efficiency"] * efficiency +
        weights["resilience"] * resilience_factor +
        weights["overhead"] * overhead_factor +
        weights["routing_quality"] * routing_quality +
        weights["delay_factor"] * delay_factor +
        weights["traffic_balance"] * traffic_balance
    )
      # Store detailed scores for reporting
    detailed_scores = {
        "efficiency": efficiency,
        "resilience": resilience_factor,
        "overhead": overhead_factor,
        "routing_quality": routing_quality,
        "delay_factor": delay_factor,
        "traffic_balance": traffic_balance,
        "final_score": score
    }
    
    return score, detailed_scores

def compare_topologies(topology_summaries):
    """Compare topologies and rank them based on their comprehensive scores.
    
    Args:
        topology_summaries: List of topology summary dictionaries
        
    Returns:
        List of dictionaries with topology ranking information
    """
    # Calculate scores for each topology
    rankings = []
    for summary in topology_summaries:
        score, detailed_scores = calculate_topology_score(summary)
        
        # Create ranking entry with all score components
        ranking_entry = {
            "topology": summary["topology"],
            "score": score,
            "detailed_scores": detailed_scores,
            # Store network characteristics for analysis
            "avg_efficiency": summary["avg_efficiency"],
            "avg_reconnections": summary["avg_reconnections"],
            "total_links_removed": summary["total_links_removed"],
            "total_links_added": summary["total_links_added"],
            "total_sent_messages": summary["total_sent_messages"],
            "total_msg_packets": summary["total_msg_packets"]
        }
        
        # Calculate additional metrics about the network
        
        # Link stability - ratio of links that remained stable
        total_link_events = summary["total_links_removed"] + summary["total_links_added"]
        if total_link_events > 0:
            link_stability = 1.0 - (summary["total_links_removed"] / total_link_events)
        else:
            link_stability = 1.0  # Perfect stability if no link changes
            
        # Network efficiency - messages per link
        if total_link_events > 0:
            messages_per_link = summary["total_sent_messages"] / total_link_events
        else:
            messages_per_link = summary["total_sent_messages"]  # All messages on stable links
        
        # Add these metrics to the ranking entry
        ranking_entry["link_stability"] = link_stability
        ranking_entry["messages_per_link"] = messages_per_link
        
        rankings.append(ranking_entry)
    
    # Sort by score (highest first)
    rankings.sort(key=lambda x: x["score"], reverse=True)
    
    # Add rank
    for i, ranking in enumerate(rankings):
        ranking["rank"] = i + 1
    
    return rankings
