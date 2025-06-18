# Wireless Network Simulation with Proactive Distance Vector Routing

This project implements a wireless sensor network simulation with a proactive distance vector routing protocol, where nodes exchange messages to perform network discovery and maintain up-to-date routing tables.

## Key Features

- **Proactive Distance Vector Routing Protocol**: Nodes exchange distance vectors with neighbors to discover optimal routes to all destinations
- **Interactive Visualizations**: Supports multiple visualization methods (Matplotlib, NetworkX, and adjacency list)
- **Network Topology Changes**: Simulates link additions, removals, and quality changes to demonstrate the self-healing nature of the protocol
- **Detailed Reporting**: Generates comprehensive reports on network structure, routing tables, and performance metrics

## Protocol Description

The implemented distance vector protocol is proactive in nature, meaning:

1. All nodes maintain complete routing tables at all times
2. Nodes exchange distance vector information with their neighbors periodically
3. When a node receives a distance vector from a neighbor, it updates its own tables if better routes are discovered
4. The protocol automatically reacts to topology changes (links added, removed, or delay changes)
5. Routing tables converge to optimal paths as nodes continue to exchange information

## How the Protocol Works

1. **Initialization**: Each node initializes its distance vector with direct connections to neighbors
2. **Information Exchange**: Nodes send their distance vectors to all neighbors
3. **Update Processing**: When a node receives a distance vector from a neighbor, it:
   - Processes the vector to see if better paths are available through this neighbor
   - Updates its own distance vector and routing table if improvements are found
4. **Convergence**: The process continues until no further updates are needed, meaning the network has converged to optimal routes
5. **Topology Changes**: If network topology changes (links added/removed), affected nodes detect the change and proactively send updates

## Running the Simulation

```bash
# Basic simulation with default 15 nodes
python simulation.py

# Simulation with specific number of nodes
python simulation.py --nodes=10

# Interactive visualization mode
python simulation.py --interactive

# Auto-install required dependencies
python simulation.py --auto-install
```

## Command Line Options

- `--nodes=<number>`: Set the number of nodes in the network
- `--interactive`, `-i`: Enable interactive visualizations
- `--auto-install`: Automatically install missing dependencies

## Project Structure

```
/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── network.py         # Network implementation with distance vector protocol
│   │   └── sensor_node.py     # Node implementation with routing logic
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── report_network.py  # Network report generation
│   └── visualization/
│       ├── __init__.py
│       ├── visualization.py   # Main visualization interface
│       └── visualization_backend.py  # Visualization implementations
├── tests/
│   └── test_suite.py          # Test cases for the network
├── output/
│   ├── reports/               # Generated network reports
│   └── visualizations/        # Generated network visualizations
├── simulation.py              # Main simulation script
└── README.md
```

## Technical Implementation Details

The distance vector protocol is implemented using the Bellman-Ford algorithm in a distributed manner:

1. Each node maintains:
   - A distance vector with costs to all destinations
   - A routing table mapping destinations to next hops and costs
   - A list of received vectors from neighbors waiting to be processed

2. The routing logic follows these principles:
   - A node's distance to itself is always 0
   - Direct connections to neighbors have costs equal to link delays
   - For other destinations, the cost is the minimum of:
     (cost to neighbor + neighbor's cost to destination) across all neighbors

3. When a node updates its distance vector, it marks itself as needing to send updates to neighbors

4. Protocol convergence is detected when no nodes have any pending updates to send

## Network Visualization

The simulation supports three types of visualizations:

1. **Matplotlib**: Node positions with connections and their delays
2. **NetworkX**: Force-directed graph showing network topology
3. **Adjacency List**: Text-based representation of the network

In interactive mode, these visualizations are displayed in separate windows that stay open until the user presses Enter.

## Example Use Cases

1. **Network Discovery**: Nodes joining the network automatically learn routes to all reachable destinations
2. **Link Failure Recovery**: When links fail, the protocol quickly finds alternate routes if available
3. **Topology Optimization**: When new links are added or improved, the protocol automatically updates to use better routes

## Requirements

- Python 3.6+
- NetworkX
- Matplotlib
- NumPy

On Windows, make sure you have tkinter installed (comes with standard Python installation).
