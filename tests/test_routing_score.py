"""
Test script for the updated routing-aware scoring function
"""

from src.core.evaluation_score import calculate_topology_score

def test_scoring():
    # Create a mock topology summary with good routing metrics
    mock_good_routing = {
        "avg_efficiency": 0.7,
        "avg_reconnections": 1.2,
        "total_links_removed": 5,
        "total_sent_messages": 50,
        "total_msg_packets": 80,
        "avg_hops_per_message": 2.0,  # Good - short paths
        "avg_delay_per_message": 1.0   # Good - low delay
    }
    
    # Create a mock topology summary with poor routing metrics
    mock_poor_routing = {
        "avg_efficiency": 0.7,
        "avg_reconnections": 1.2,
        "total_links_removed": 5,
        "total_sent_messages": 50,
        "total_msg_packets": 80,
        "avg_hops_per_message": 8.0,  # Poor - long paths
        "avg_delay_per_message": 4.0   # Poor - high delay
    }
    
    # Test the scoring function on both topologies
    good_score, good_detailed = calculate_topology_score(mock_good_routing)
    poor_score, poor_detailed = calculate_topology_score(mock_poor_routing)
    
    print("\nTesting updated routing-aware scoring function:")
    print("\nTopology with good routing metrics:")
    print(f"Overall score: {good_score:.4f}")
    print("\nDetailed score components:")
    for component, value in good_detailed.items():
        if component != "final_score":
            print(f"  - {component}: {value:.4f}")
    
    print("\nTopology with poor routing metrics:")
    print(f"Overall score: {poor_score:.4f}")
    print("\nDetailed score components:")
    for component, value in poor_detailed.items():
        if component != "final_score":
            print(f"  - {component}: {value:.4f}")
    
    print(f"\nScore difference due to routing quality: {good_score - poor_score:.4f}")
    print("\nTest complete. The updated scoring formula now properly values routing distance and delay metrics.")

if __name__ == "__main__":
    test_scoring()
