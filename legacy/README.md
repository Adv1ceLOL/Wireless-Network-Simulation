## Legacy Directory

This directory preserves superseded implementations retained for historical traceability only. They are excluded from current documentation, execution paths, and tests.

### Files
`simulation_old.py` – Original version including both static and dynamic modes; static mode was removed from maintained branch. Uses earlier argument naming and less granular message accounting.

`simulation_clean.py` – Intermediate refactoring with reduced parameter set (`--iterations` vs. current `--time-steps`). Functionally subsumed by `simulation.py`.

### Current Policy
- Do not modify or extend these files.
- Do not base new experiments on them; rely on `simulation.py` and modules in `src/core/`.
- Static mode is intentionally unsupported in the active code base.

End of legacy note.
