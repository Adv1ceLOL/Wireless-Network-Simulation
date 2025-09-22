## Test Suite Overview

This directory contains Python scripts exercising core simulation, routing, evaluation scoring, efficiency measurement, and convergence behaviour. No external test framework is required; each file is directly executable with the Python interpreter.

### Categories
Efficiency and Protocol:
- `test_efficiency_optimization.py` – validates optimisation logic (incremental updates, reduced unnecessary route discovery messages).
- `test_efficiency_simple.py` – basic sanity checks of efficiency accounting.
- `test_efficiency_summary.py` – summarises efficiency related outcomes over representative parameter sets.
- `test_protocol_efficiency.py` – verifies efficiency ratio under controlled probability inputs.

Routing and Scoring:
- `test_routing_score.py` – evaluates routing quality metrics used in evaluation scoring.
- `test_scoring.py` – checks composite scoring consistency.

Network / Simulator Integrity:
- `test_network_simulator.py` – network generation, connectivity, link invariants.
- `test_simulator.py` – end‑to‑end single simulation flow.
- `test_integration.py` – broader integration covering message counters and path formation.

Convergence / Iterations:
- `test_iterations.py` – convergence iteration counts and reconvergence after topology changes.

Utility / Regression:
- `test_simple.py` – minimal structural assertions.
- `test_fix.py` – regression for previously identified issues.
- `test_suite.py` – orchestration script invoking a representative subset / all tests.

### Running Tests
Examples (from project root):
```
python tests/test_simple.py
python tests/test_network_simulator.py
python tests/test_efficiency_optimization.py
```
Run aggregated suite:
```
python tests/test_suite.py
```

### Requirements
- Dependency installation via `pip install -r requirements.txt` beforehand.
- Source directory layout unchanged (`src/core/`, main `simulation.py`).

### Notes
- Tests are intentionally lightweight to remain portable without pytest/unittest harness overhead.
- Randomness: where determinism is required, scripts set fixed seeds; otherwise statistical expectations are checked with tolerance.

End of test documentation.
