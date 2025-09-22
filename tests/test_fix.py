#!/usr/bin/env python3
"""
Test script to verify that different parameters produce different results.
"""

import subprocess
import sys
import re
from typing import Dict, Any

def run_simulation(args: str) -> Dict[str, Any]:
    """Run simulation with given arguments and extract key metrics."""
    cmd = f"{sys.executable} simulation.py {args}"
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        output = result.stdout
        
        # Extract key metrics from output
        metrics = {}
        
        # Extract message counts
        hello_match = re.search(r'Hello Messages: (\d+)', output)
        topology_match = re.search(r'Topology Discovery Messages: (\d+)', output)
        route_match = re.search(r'Route Discovery Control Packets: (\d+)', output)
        data_match = re.search(r'Data Packets Forwarded: (\d+)', output)
        total_match = re.search(r'Total Message Exchanges: (\d+)', output)
        
        # Extract efficiency
        efficiency_match = re.search(r'Protocol Efficiency: ([\d.]+)', output)
        
        # Extract simulation stats
        requests_match = re.search(r'Packet requests: (\d+)', output)
        success_match = re.search(r'Successful transmissions: (\d+)', output)
        links_removed_match = re.search(r'Links removed: (\d+)', output)
        links_added_match = re.search(r'Links added: (\d+)', output)
        
        metrics = {
            'hello_msgs': int(hello_match.group(1)) if hello_match else 0,
            'topology_msgs': int(topology_match.group(1)) if topology_match else 0,
            'route_msgs': int(route_match.group(1)) if route_match else 0,
            'data_packets': int(data_match.group(1)) if data_match else 0,
            'total_msgs': int(total_match.group(1)) if total_match else 0,
            'efficiency': float(efficiency_match.group(1)) if efficiency_match else 0.0,
            'requests': int(requests_match.group(1)) if requests_match else 0,
            'successful': int(success_match.group(1)) if success_match else 0,
            'links_removed': int(links_removed_match.group(1)) if links_removed_match else 0,
            'links_added': int(links_added_match.group(1)) if links_added_match else 0,
            'output_length': len(output)
        }
        
        print(f"Extracted metrics: {metrics}")
        return metrics
        
    except subprocess.TimeoutExpired:
        print("Simulation timed out!")
        return {}
    except Exception as e:
        print(f"Error running simulation: {e}")
        return {}

def main():
    print("Testing that different parameters produce different results...")
    
    # Test case 1: High request probability, no topology changes
    print("\n" + "="*60)
    print("Test 1: High request rate, no topology changes")
    metrics1 = run_simulation("--nodes=10 --p-new=0.0 --p-fail=0.0 --p-request=0.9 --time-steps=20")
    
    # Test case 2: High topology changes, low request rate  
    print("\n" + "="*60)
    print("Test 2: High topology changes, low request rate")
    metrics2 = run_simulation("--nodes=10 --p-new=0.6 --p-fail=0.6 --p-request=0.2 --time-steps=20")
    
    # Test case 3: Medium values for comparison
    print("\n" + "="*60)
    print("Test 3: Medium values")
    metrics3 = run_simulation("--nodes=10 --p-new=0.3 --p-fail=0.3 --p-request=0.5 --time-steps=20")
    
    # Compare results
    print("\n" + "="*60)
    print("COMPARISON RESULTS:")
    print("="*60)
    
    def print_comparison(metric_name: str):
        val1 = metrics1.get(metric_name, 0)
        val2 = metrics2.get(metric_name, 0)
        val3 = metrics3.get(metric_name, 0)
        print(f"{metric_name:20} | Test1: {val1:8} | Test2: {val2:8} | Test3: {val3:8}")
        
        # Check if values are different
        if val1 == val2 == val3:
            print(f"  WARNING: All values are identical for {metric_name}!")
        elif val1 != val2 or val2 != val3 or val1 != val3:
            print(f"  GOOD: Values differ for {metric_name}")
        
    print(f"{'Metric':<20} | {'Test1':<8} | {'Test2':<8} | {'Test3':<8}")
    print("-" * 60)
    
    print_comparison('requests')
    print_comparison('data_packets')
    print_comparison('total_msgs')
    print_comparison('links_removed')
    print_comparison('links_added')
    print_comparison('efficiency')
    
    # Overall assessment
    print("\n" + "="*60)
    different_metrics = 0
    total_metrics = 6
    
    for metric in ['requests', 'data_packets', 'total_msgs', 'links_removed', 'links_added', 'efficiency']:
        val1 = metrics1.get(metric, 0)
        val2 = metrics2.get(metric, 0)
        val3 = metrics3.get(metric, 0)
        if not (val1 == val2 == val3):
            different_metrics += 1
    
    print(f"OVERALL RESULT: {different_metrics}/{total_metrics} metrics show variation")
    
    if different_metrics >= 4:
        print("✅ PASS: Parameters are having the expected effect!")
    elif different_metrics >= 2:
        print("⚠️  PARTIAL: Some parameters are working, but there may still be issues")
    else:
        print("❌ FAIL: Parameters are not having sufficient effect")
    
    return different_metrics >= 4

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
