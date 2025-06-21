import os
import random
import math

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
