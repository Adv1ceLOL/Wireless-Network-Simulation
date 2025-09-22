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
            "resilience": 0.20,
            "overhead": 0.15,
            "routing_quality": 0.20,
            "delay_factor": 0.10,
            "traffic_balance": 0.10
        }
    
    efficiency = topology_summary["avg_efficiency"]
    
    reconnections = topology_summary["avg_reconnections"]
    links_removed = topology_summary["total_links_removed"]
    resilience_base = max(0.1, 1.0 - (reconnections/5.0))
    link_failure_impact = max(0.1, 1.0 - (math.log(links_removed + 1) / 10.0))
    resilience_factor = (resilience_base + link_failure_impact) / 2.0
    
    data_messages = topology_summary["total_sent_messages"]
    if data_messages == 0:
        overhead_factor = 0
    else:
        control_messages = topology_summary["total_msg_packets"] - data_messages
        overhead_ratio = control_messages / max(1, data_messages)
        overhead_factor = 1.0 / (1.0 + (overhead_ratio / 3.0))
    
    avg_hops = topology_summary.get("avg_hops_per_message", 0)
    successful_transmissions = topology_summary["total_sent_messages"]
    
    if successful_transmissions == 0 or avg_hops == 0:
        routing_quality = 0
    else:
        routing_quality = max(0.1, 1.0 - (avg_hops / 14.0))
    
    avg_delay = topology_summary.get("avg_delay_per_message", 0)
    
    if successful_transmissions == 0 or avg_delay == 0:
        delay_factor = 0
    else:
        delay_factor = max(0.1, 1.0 - (avg_delay / 5.0))
    
    if data_messages > 0:
        traffic_ratio = data_messages / topology_summary["total_msg_packets"]
        traffic_balance = 1.0 / (1.0 + math.exp(-10 * (traffic_ratio - 0.1)))
    else:
        traffic_balance = 0
    
    score = (
        weights["efficiency"] * efficiency +
        weights["resilience"] * resilience_factor +
        weights["overhead"] * overhead_factor +
        weights["routing_quality"] * routing_quality +
        weights["delay_factor"] * delay_factor +
        weights["traffic_balance"] * traffic_balance
    )
    
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
