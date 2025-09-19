# Test Suite Documentation

This directory contains all test files for the Wireless Sensor Network Simulation project.

## Test Categories

### Efficiency Optimization Tests
- `test_efficiency_optimization.py` - Comprehensive test suite for efficiency optimization feature
- `test_efficiency_simple.py` - Simple verification test for efficiency optimization
- `test_efficiency_summary.py` - Summary and documentation of efficiency optimization tests
- `test_protocol_efficiency.py` - Protocol efficiency analysis tests

### Integration Tests
- `test_integration.py` - Integration tests for the complete system
- `test_suite.py` - Main test suite runner

### Network and Routing Tests
- `test_network_simulator.py` - Network simulation tests
- `test_routing_score.py` - Routing algorithm scoring tests
- `test_scoring.py` - General scoring mechanism tests
- `test_simulator.py` - Simulator functionality tests

### Utility Tests
- `test_simple.py` - Simple unit tests
- `test_iterations.py` - Iteration and convergence tests
- `test_fix.py` - Bug fix verification tests

## Running Tests

To run all tests from the project root directory:

```bash
# Run individual test files
python tests/test_efficiency_optimization.py
python tests/test_efficiency_simple.py
python tests/test_integration.py

# Run the main test suite
python tests/test_suite.py
```

## Test Requirements

All tests assume the following project structure:
- `src/` - Source code directory
- `simulation.py` - Main simulation entry point
- Proper Python environment with all dependencies installed

## Recent Additions

- **Efficiency Optimization Tests**: Comprehensive testing of the `ignore_initial_route_discovery` feature
- **Protocol Efficiency Analysis**: Tests verifying protocol efficiency calculations and optimizations
