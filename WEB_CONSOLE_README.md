## Web Console Documentation

This document describes only the browser-based console. High-level system details are in the root `README.md`.

### 1. Purpose
The web console provides an interactive environment to inspect, step, and manipulate the dynamic wireless sensor network. It is intended for exploratory analysis (routing convergence, topology evolution, efficiency impacts of link changes) and for demonstration purposes.

### 2. Launch Methods
Recommended (dependency check + fixed port 5001):
```
python start_web_console.py
```
Direct (custom host/port):
```
python web_console.py --host 127.0.0.1 --port 5000
```
Access via browser at the indicated address (default http://localhost:5000 or http://localhost:5001).

### 3. Core Features
- Network creation: specify node count and area size; generator ensures initial connectivity.
- Parameter adjustment: p_request, p_fail, p_new, time_steps may be updated between steps.
- Step execution: single discrete step or continuous auto‑play (with adjustable delay).
- Topology modification: add/remove links (additions validated by mutual transmission range condition).
- Routing inspection: per‑node routing tables, distance vectors, connection lists, message counters.
- Statistics panel: requests, successes, failures, added/removed links, reconvergence iterations, cumulative delay, total messages.
- History navigation: move backward/forward across previously recorded states; jump to first/last step.
- Export: JSON snapshot of entire state or plain text report summarising parameters, topology and counters.
- Connectivity check: reports unreachable pairs and connectivity ratio.

### 4. Typical Workflow
1. Create network with chosen node number (e.g. 10–30) and area size.
2. Execute several manual steps to observe control message accumulation.
3. Enable auto‑play to observe probabilistic failures/additions and reconvergence iteration counts.
4. Pause, inspect routing tables for selected nodes, optionally remove or add a link.
5. Export report for documentation.

### 5. Controls Summary
- Create Network: allocate and initialise topology (resets history).
- Step Forward: execute exactly one dynamic step.
- Auto Play / Stop: start/stop continuous progression at set delay.
- Add Link / Remove Link: manipulate topology for currently selected node pair and (for addition) chosen delay.
- Parameter Update: adjust probabilities without recreating network.
- Show Routing Info: fetch detailed routing tables and vectors for selected nodes.
- Navigation: first / back / forward / last / goto index.

### 6. Events in a Simulation Step
Order of operations (conceptual):
1. Hello message exchange (counts per neighbor; interval configurable in core CLI variant).
2. Probabilistic link failure (uniform selection among existing links).
3. Probabilistic link addition (biased to reconnect isolated nodes; saturation scaling of p_new).
4. Probabilistic data transmission request; attempt routing; record success/failure and path delay.

### 7. Exported Data
JSON export contains: parameters, full node list (position, range, connections), links, history entries (events + snapshots), statistics, per-node message counts. Text report summarises counts and basic topology listing.

### 8. Troubleshooting
Port already in use: change `--port` or terminate prior process (`lsof -ti:5000 | xargs kill -9` on macOS/Linux).  
Blank page / JS errors: open browser console, ensure static files served; refresh after network (re)creation.  
No routing tables updating: ensure a network was created first; verify probabilities not all set to zero (which may yield trivial steps).

### 9. Performance Notes
Larger networks (>30 nodes) increase DOM and force‑layout complexity. To maintain responsiveness reduce auto‑play speed or temporarily avoid frequent topology modifications.

### 10. Scope Limitation
Web console presently targets distance‑vector protocol only; alternative protocols would require additional server events and client visual encodings.

End of web console documentation.
