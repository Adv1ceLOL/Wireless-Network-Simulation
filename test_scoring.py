"""
Test script for the updated scoring function
"""

from src.core.evaluation import calculate_topology_score

# Create a mock topology summary
mock_summary = {
    "avg_efficiency": 0.7,
    "avg_reconnections": 1.2,
    "total_links_removed": 5,
    "total_sent_messages": 50,
    "total_msg_packets": 80,
    "avg_hops_per_message": 3.2,
    "avg_delay_per_message": 1.5
}

# Test the scoring function
score, detailed = calculate_topology_score(mock_summary)

print("\nTesting updated scoring function:")
print(f"Overall score: {score:.4f}")
print("\nDetailed score components:")
for component, value in detailed.items():
    if component != "final_score":
        print(f"  - {component}: {value:.4f}")

print("\nTest complete. The updated scoring formula now includes routing quality and delay metrics.")
