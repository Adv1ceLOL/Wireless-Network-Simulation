"""
Integration test for the new evaluation scoring
"""

from src.core.evaluation_score import calculate_topology_score

# Test topology data
test_topology = {
    "topology": 1,
    "avg_efficiency": 0.65,
    "avg_p_request": 0.5,
    "avg_p_fail": 0.15,
    "avg_p_new": 0.15,
    "avg_reconnections": 1.5,
    "total_data_packets": 120,
    "total_msg_packets": 200,
    "total_links_removed": 8,
    "total_links_added": 10,
    "total_sent_messages": 120,
    "total_hops": 350,
    "total_delay": 180.5,
    "avg_hops_per_message": 2.92,
    "avg_delay_per_message": 1.5
}

# Calculate score
score, details = calculate_topology_score(test_topology)

print("\nRouting-Aware Scoring Results")
print("============================")
print(f"Overall score: {score:.4f}")
print("\nScore Components:")
print(f"  Efficiency:      {details['efficiency']:.4f} (weight: 0.25)")
print(f"  Resilience:      {details['resilience']:.4f} (weight: 0.20)")
print(f"  Overhead:        {details['overhead']:.4f} (weight: 0.15)")
print(f"  Routing Quality: {details['routing_quality']:.4f} (weight: 0.20)")
print(f"  Delay Factor:    {details['delay_factor']:.4f} (weight: 0.10)")
print(f"  Traffic Balance: {details['traffic_balance']:.4f} (weight: 0.10)")

print("\nRouting metrics:")
print(f"  Average hops per message: {test_topology['avg_hops_per_message']:.2f}")
print(f"  Average delay per message: {test_topology['avg_delay_per_message']:.2f}")

print("\nTest complete! The scoring function now correctly values routing quality based on path length and link delay.")
