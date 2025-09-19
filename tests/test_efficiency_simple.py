#!/usr/bin/env python3
"""
Simple test to verify efficiency optimization in deterministic_scenario.py
Tests by modifying the ignore_initial_route_discovery parameter directly.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.deterministic_scenario import main as scenario_main
from src.core.evaluation import get_route_discovery_msg_count, get_protocol_efficiency


def test_scenario_with_optimization():
    """Test scenario_main with optimization enabled"""
    print("🧪 Testing scenario with optimization ENABLED...")
    
    network = scenario_main(
        n_nodes=5,
        time_steps=3,
        p_request=0.5,
        p_fail=0.0,
        p_new=0.0,
        verbose=False,
        interactive=False,
        ignore_initial_route_discovery=True,  # OPTIMIZATION ENABLED
        random_seed=123
    )
    
    route_discovery = get_route_discovery_msg_count(network)
    efficiency = get_protocol_efficiency(network)
    
    print(f"✅ Route discovery messages: {route_discovery}")
    print(f"✅ Protocol efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")
    
    return route_discovery, efficiency


def test_scenario_without_optimization():
    """Test scenario_main with optimization disabled"""
    print("\n🧪 Testing scenario with optimization DISABLED...")
    
    network = scenario_main(
        n_nodes=5,
        time_steps=3,
        p_request=0.5,
        p_fail=0.0,
        p_new=0.0,
        verbose=False,
        interactive=False,
        ignore_initial_route_discovery=False,  # OPTIMIZATION DISABLED
        random_seed=123
    )
    
    route_discovery = get_route_discovery_msg_count(network)
    efficiency = get_protocol_efficiency(network)
    
    print(f"✅ Route discovery messages: {route_discovery}")
    print(f"✅ Protocol efficiency: {efficiency:.4f} ({efficiency*100:.2f}%)")
    
    return route_discovery, efficiency


if __name__ == "__main__":
    print("="*60)
    print("EFFICIENCY OPTIMIZATION VERIFICATION")
    print("="*60)
    print("Testing deterministic_scenario.py with and without optimization")
    
    # Test with optimization enabled
    route_with_opt, eff_with_opt = test_scenario_with_optimization()
    
    # Test with optimization disabled  
    route_without_opt, eff_without_opt = test_scenario_without_optimization()
    
    # Compare results
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    
    print(f"Route Discovery Messages:")
    print(f"  With optimization:    {route_with_opt}")
    print(f"  Without optimization: {route_without_opt}")
    print(f"  Difference:           {route_without_opt - route_with_opt}")
    
    print(f"\nProtocol Efficiency:")
    print(f"  With optimization:    {eff_with_opt:.4f} ({eff_with_opt*100:.2f}%)")
    print(f"  Without optimization: {eff_without_opt:.4f} ({eff_without_opt*100:.2f}%)")
    print(f"  Improvement:          {eff_with_opt - eff_without_opt:.4f} ({(eff_with_opt - eff_without_opt)*100:.2f} percentage points)")
    
    print(f"\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    if route_with_opt == 0:
        print("✅ PASS: Route discovery messages reset to 0 with optimization")
    else:
        print("❌ FAIL: Route discovery messages not reset properly")
    
    if route_without_opt > route_with_opt:
        print("✅ PASS: Without optimization has more route discovery messages")
    else:
        print("❌ FAIL: Optimization not reducing route discovery messages")
    
    if eff_with_opt > eff_without_opt:
        print("✅ PASS: Efficiency is higher with optimization")
    else:
        print("❌ FAIL: Optimization not improving efficiency")
    
    if route_with_opt == 0 and route_without_opt > 0 and eff_with_opt > eff_without_opt:
        print("\n🎉 SUCCESS: Efficiency optimization is working correctly!")
    else:
        print("\n⚠️  WARNING: Efficiency optimization may not be working as expected")
