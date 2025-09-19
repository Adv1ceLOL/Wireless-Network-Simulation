# Legacy Files

This directory contains older versions and deprecated simulation files that are kept for reference.

## Files

### simulation_old.py
- **Status**: Deprecated
- **Description**: Original simulation implementation with both static and dynamic modes
- **Replaced by**: `../simulation.py` (current implementation focuses on dynamic scenarios only)
- **Key differences**: 
  - Contains static mode functionality (removed in current version)
  - Uses older parameter structure
  - Less optimized message counting

### simulation_clean.py
- **Status**: Redundant
- **Description**: Cleaned version of simulation.py with reduced parameters
- **Replaced by**: `../simulation.py` (current implementation with full feature set)
- **Key differences**:
  - Uses `--iterations` instead of `--time-steps`
  - Missing some dynamic simulation parameters
  - Simplified argument parsing

## Migration Notes

If you need to reference or restore functionality from these legacy files:

1. **Static Mode**: The current implementation focuses on dynamic scenarios only. Static mode functionality can be found in `simulation_old.py`
2. **Parameter Names**: The current implementation uses `--time-steps` instead of `--iterations`
3. **Feature Set**: The current implementation includes all efficiency optimizations and message counting improvements

## Deprecation Timeline

- `simulation_old.py`: Deprecated when dynamic-only implementation was finalized
- `simulation_clean.py`: Deprecated when full parameter set was standardized in main simulation.py
