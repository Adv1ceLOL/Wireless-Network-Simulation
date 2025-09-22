<div align="center">
<h1>Wireless Sensor Network Simulator</h1>
<p>Formal documentation for the university assignment: probabilistic simulation and evaluation of a proactive distance‑vector routing protocol in a dynamic wireless sensor network.</p>
</div>

---

<div align="center">

##  **[→ View Efficiency Analysis & Experimental Results ](considerations.md)**
##  **[→ View Proactive vs Reactive Protocol Comparison ](proactive_vs_reactive_analysis.md)**


</div>


## 1. Assignment Statement (Summary)
We implement a wireless sensor network with N nodes. Links are weighted with delays in [0,1]. A proactive distance‑vector routing protocol establishes and maintains routing tables. At each discrete time step t:
1. With probability p_request a data transmission request (s → d) is generated.
2. With probability p_fail an existing link is removed.
3. With probability p_new a new feasible bidirectional link appears.
4. Nodes exchange periodic hello / maintenance messages and propagate topology changes so that routing tables converge within the same time step abstraction.

The system counts (a) control messages (hello, topology / distance‑vector exchanges, route maintenance) and (b) data packet forwards. Efficiency is defined as:

  efficiency = (number of data packets) / (total number of packets)

The aim is to study how varying p_request, p_fail, p_new (typically ≤ 0.3) influences efficiency and related metrics. We additionally explore convergence iterations after topology changes and delay characteristics of chosen paths.

---

## 2. Implemented Scope
Implemented features (current code base):
- Random connected network generation with enforced absence of isolated nodes.
- Weighted undirected links (symmetric delay in [0,1]).
- Proactive distance‑vector protocol with convergence iterations counting and incremental update optimisation.
- Dynamic topology evolution (probabilistic link failures and additions) with feasibility checks (mutual transmission range requirement).
- Probabilistic traffic generation (data requests) and path simulation using current routing tables.
- Message accounting by type: hello, topology setup, route discovery (DV exchanges), data packets.
- Efficiency computation, delay accumulation, reconvergence iteration tracking.
- Optional comprehensive evaluation mode over multiple random topologies and iterations with scoring/report output.
- Deterministic / scripted scenario entry point (`deterministic_scenario.py`) used by `simulation.py`.
- Web console (interactive browser UI) providing step execution, auto‑play, parameter updates, topology modifications, routing inspection, export, and connectivity checks.
- Visualization backends (matplotlib / NetworkX / adjacency list, plus browser D3 interface).

Removed / deprecated (not documented further here): legacy static mode variants and earlier simplified parameter sets (`legacy/`).

---

## 3. Project Structure (Relevant Directories)
```
src/core/              Core simulation logic (network, nodes, evaluation, scenarios)
src/visualization/     Image / graph generation helpers
src/reporting/         Report generation utilities
simulation.py          Main CLI entry point (dynamic simulation + evaluation)
web_console.py         Web interface server (Flask + Socket.IO)
start_web_console.py   Convenience launcher with dependency check
tests/                 Test scripts (unit, integration, efficiency, scoring)
output/visualizations/ Generated PNG images (topology views)
output/reports/        Text reports (network and evaluation)
legacy/                Archived deprecated implementations
scenarios/             JSON scenario definitions (optional future use)
```

---

## 4. Core Architecture Overview
Component summary:
- SensorNode: maintains position, transmission range, connections (neighbor → delay), distance vector, routing table, counters.
- SensorNetwork: container for nodes, random network generation ensuring connectivity, routing protocol execution, topology change handling (full and incremental), message counting, path simulation.
- Distance‑Vector Protocol: iterative dissemination of distance vectors until no further improvements; incremental variant triggered by specific link events reduces unnecessary global exchanges.
- Dynamic Step Logic (in deterministic scenario pathway and web console): executes in order: hello messaging, probabilistic failure, probabilistic addition (with isolation‑aware bias), probabilistic data request and delivery attempt.
- Evaluation Module: runs batches across random topologies, aggregates efficiency and other metrics, writes report.
- Reporting: generation of per‑simulation network report and evaluation report summarising metrics.

Message Types Counted:
1. hello_msg_count – neighbor liveness / maintenance each step (configurable interval via `--hello-interval`).
2. topology_msg_count – initial topology setup messages (one per node at protocol start).
3. route_discovery_msg_count – distance vector updates actually sent (suppressed if no meaningful change).
4. data_packet_count – successful data transmissions (counted at source side to avoid per‑hop inflation).

Incremental Optimisation: on link add/remove/update the protocol limits propagation to affected subgraph, reducing route discovery messages.

---

## 5. Command Line Interface (Current Parameters)
Run:
```
python simulation.py [options]
```

| Option | Default | Purpose |
|--------|---------|---------|
| --nodes INT | 10 | Number of nodes in initial random connected network |
| --seed INT | None | Reproducibility seed for topology generation |
| --time-steps INT | 100 | Number of dynamic steps to execute |
| --p-request FLOAT | 0.3 | Probability of generating one data request in a step |
| --p-fail FLOAT | 0.1 | Probability of removing a random existing link |
| --p-new FLOAT | 0.1 | Base probability of adding a feasible new link (scaled by saturation) |
| --hello-interval INT | 1 | Steps between hello message exchanges (1 = every step) |
| --delay FLOAT | 0.0 | Real time sleep between steps (seconds) |
| --no-interactive | (flag) | Disable matplotlib/networkx static visual outputs during run |
| --verbose | (flag) | Verbose protocol/log output |
| --evaluation | (flag) | Run multi‑topology evaluation instead of single simulation |
| --eval-topologies INT | 3 | Number of random topologies in evaluation mode |
| --eval-iterations INT | 50 | Iterations per topology in evaluation mode |

Notes:
- Interactive plotting is disabled by default in current main script; pass nothing for standard run, add custom visualization scripts if needed.
- Efficiency and message counts are printed / reported at completion.

---

## 6. Typical Usage Examples
Basic simulation (default parameters):
```
python simulation.py
```

Custom probabilities and limited steps:
```
python simulation.py --nodes 15 --time-steps 60 --p-request 0.4 --p-fail 0.05 --p-new 0.08
```

Change hello interval (reduce control overhead):
```
python simulation.py --hello-interval 3
```

Evaluation mode (multiple topologies):
```
python simulation.py --evaluation --eval-topologies 5 --eval-iterations 40 --p-request 0.35
```

Seeded reproducible topology:
```
python simulation.py --seed 42 --nodes 12
```

Disable extra visualizations and enable verbose protocol logs:
```
python simulation.py --no-interactive --verbose
```

---

## 7. Web Console (Browser Interface)
Two launch methods:
1. Convenience script (installs dependencies if missing, port 5001):
```
python start_web_console.py
```
2. Direct server run (default port 5000):
```
python web_console.py --host 127.0.0.1 --port 5000
```

Access: http://localhost:5000 (or 5001 if using the starter script).

Capabilities:
- Create network with chosen node count and area size.
- Adjust p_request, p_fail, p_new, time_steps during execution.
- Single‑step execution or auto‑play with configurable delay.
- Add/remove links (validated by mutual range) with automatic incremental reconvergence.
- Inspect per‑node routing tables, distance vectors, message counters.
- View statistics: requests, successes/failures, reconvergence iterations, link changes, cumulative delay.
- Export JSON snapshot or textual report.
- Navigate through recorded history steps (forward/back / goto).
- Connectivity check (reports unreachable pairs and ratio).

When to prefer the web console: exploratory analysis, manual topology experimentation, routing inspection, didactic demonstration of convergence and isolation effects.

---

## 8. Output Artifacts
Directory `output/visualizations/` – generated PNGs (adjacency, topology).  
Directory `output/reports/` – textual network report (`network_report.txt` etc.) and evaluation report (`evaluation_report.txt`).

Reports include: node counts, link counts, convergence iterations, per‑type message totals, efficiency, and route quality metrics (where produced by evaluation module).

---

## 9. Metrics and Efficiency Definition
Let:
- D = data_packet_count
- H = hello_msg_count
- T = topology_msg_count
- R = route_discovery_msg_count
- Total = D + H + T + R

Efficiency = D / Total

Supporting metrics (evaluation mode may derive additional weighted scores: resilience, overhead, routing quality, delay factor, balance). Only efficiency is fundamental to the assignment; other composite scores are auxiliary analytic aids.

---

## 10. Testing
Tests are plain Python scripts without external framework dependency. Run individually:
```
python tests/test_simple.py
python tests/test_simulator.py
python tests/test_network_simulator.py
python tests/test_iterations.py
python tests/test_protocol_efficiency.py
```

Run aggregate suite:
```
python tests/test_suite.py
```

Purpose by category:
- Simple / smoke: structural correctness, basic counts.
- Network / simulator: topology generation, connectivity, routing path validity.
- Efficiency / protocol: message accounting, ratio computation under varied probabilities.
- Iterations: convergence behaviour, reconvergence iterations after changes.
- Scoring: evaluation scoring integrity.

---

## 11. Installation and Environment
Requirements file lists Python dependencies. Minimal steps:
```
python -m venv venv
source venv/bin/activate  (Linux/macOS)
pip install -r requirements.txt
```
Optional visualization backends (if not already present) may include matplotlib, networkx, Pillow.

If GUI backend issues occur (e.g. macOS / headless): limit to non-interactive mode (`--no-interactive`) or install an appropriate backend (Tk / Qt) if interactive windows are re‑enabled in future extensions.

---

## 12. Design Decisions and Rationale
Connectivity Enforcement: ensures experimental variance originates from dynamic evolution, not initial partitioning.
Mutual Transmission Range Constraint for New Links: models symmetric feasible wireless links (bidirectional reliability requirement).
Incremental Distance‑Vector Update: reduces control overhead; only nodes flagged `update_needed` disseminate changes, reflecting realistic triggered updates.
Hello Interval Parameter: allows experiments on control overhead vs. freshness; default conservative (every step) but adjustable.
Message Counting Granularity: separates topology establishment, maintenance, update dissemination, and data to isolate overhead sources.
Efficiency Definition: aligns strictly with assignment fraction (data / total) without weighting.

---


## 13. Legacy Directory Policy
`legacy/` retains superseded prototypes (`simulation_old.py`, `simulation_clean.py`). They are excluded from active documentation and testing. Kept only for traceability of evolution (parameter naming, static mode). New development should target `simulation.py` and `src/core/`.

---

## 14. Reproducibility Guidelines
For comparable experiments across parameter sets:
1. Fix a random seed (`--seed`).
2. Record (nodes, p_request, p_fail, p_new, hello-interval, time-steps).
3. Capture resulting totals from network and evaluation reports.
4. Avoid mixing incremental optimisation code changes mid‑series; tag commit before batch runs.

---

## 15. How to Extend
To add a new routing protocol:
1. Abstract routing operations behind an interface (initialisation, update dissemination, path computation).
2. Introduce protocol selection flag (e.g. `--protocol distance_vector|link_state`).
3. Maintain per‑protocol message counters for fair efficiency comparison.
4. Reuse dynamic step driver (hello + events + data) with protocol‑specific update hooks.

---

## 16. Academic Integrity Note
This document is intentionally formal, concise, and free of stylistic embellishments or emojis to conform to academic submission standards. All explanatory sections focus on factual implementation details and experimental methodology.

---

## 17. Acknowledgements
Course context: Internet of Things, Sapienza Università di Roma. The initial distance‑vector concept and random topology generation were inspired in part by publicly available educational examples (referenced repository in assignment brief). All subsequent architectural integration, optimisation and web console implementation performed in this project context.

---

End of documentation.
