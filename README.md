# 🌐 Wireless Sensor Network Simulator

A comprehensive simulator implementing **proactive distance vector routing protocol** for wireless sensor networks. This simulator tracks hello messages, models dynamic topology changes, and measures protocol efficiency according to academic networking research standards.

## 🎯 Four Simulation Modes Explained

### 1. 🔧 **Basic Mode** (Default) - Protocol Testing
```bash
python simulation.py
```
**What it does:**
- Creates a 15-node wireless network with random topology
- Runs distance vector routing protocol with hello messages
- Tracks all message types: hello, topology, route discovery, and data packets
- Calculates protocol efficiency (data packets / total packets)

**What to expect:**
```
Message Breakdown:
- Hello Messages: 28 (37.8%) - neighbor discovery
- Topology Messages: 15 (20.3%) - route updates  
- Route Discovery: 25 (33.8%) - initial convergence
- Data Packets: 6 (8.1%) - actual payload
Protocol Efficiency: 8.11%
```

### 2. ⚡ **Dynamic Mode** - Network Changes Over Time
```bash
python simulation.py --dynamic --time-steps=20
```
**What it does:**
- Network topology changes every time step (links fail/appear)
- Protocol automatically reconverges after each change
- Simulates real wireless environment with connectivity issues
- Tracks network adaptation performance

**What to expect:**
```
Dynamic Scenario Summary:
Time steps: 20
Link failures: 3 (p_fail=0.1)
New links: 2 (p_new=0.1) 
Data requests: 6/20 (p_request=0.3)
Average reconvergence: 2.1 iterations
Final efficiency: 3.45%
```

### 3. 📊 **Evaluation Mode** - Research Analysis
```bash
python simulation.py --evaluation
```
**What it does:**
- Tests multiple random network topologies (default: 5)
- Runs multiple iterations per topology with varied parameters
- Compares efficiency across different network configurations
- Generates academic research-style performance reports

**What to expect:**
```
Protocol Evaluation Report:
Topology 1: 3.24% efficiency (399 total packets)
Topology 2: 4.12% efficiency (185 total packets)
Topology 3: 2.87% efficiency (210 total packets)
Overall average: 3.41% efficiency
Best performing topology saved for analysis
```

### 4. 🎨 **Interactive Mode** - Visual Network Display
```bash
python simulation.py --interactive
```
**What it does:**
- Same as Basic Mode PLUS real-time network visualizations
- Shows network topology graphs as they update
- Displays routing tables and message flows visually
- Great for understanding how the protocol works

**What to expect:**
- Pop-up windows with network graphs
- Node positions and connections visualized
- Real-time updates as protocol converges

## ⚙️ Quick Start Guide

### Basic Testing
```bash
# Test with 10 nodes (faster)
python simulation.py --nodes=10

# Test protocol efficiency
python simulation.py --nodes=5

# View network with visualizations
python simulation.py --interactive --nodes=8
```

### Dynamic Network Testing
```bash
# Light network changes (good efficiency)
python simulation.py --dynamic --p-fail=0.05 --p-new=0.05

# Heavy network changes (realistic mobile networks)
python simulation.py --dynamic --p-fail=0.2 --p-new=0.2 --time-steps=10

# High data activity
python simulation.py --dynamic --p-request=0.8
```

### Research & Evaluation
```bash
# Quick evaluation
python simulation.py --evaluation --topologies=2 --iterations=5

# Comprehensive research analysis
python simulation.py --evaluation --topologies=10 --iterations=20
```

## 📋 Academic Requirements Implementation

This simulator implements the exact requirements from academic networking research:

### ✅ **Core Requirements Met:**
1. **Wireless sensor network with N nodes** - ✓ Configurable network size
2. **Weighted links with delays 0-1** - ✓ All delays constrained to 0.0-1.0 seconds
3. **Proactive routing protocol** - ✓ Distance vector with Bellman-Ford algorithm
4. **Hello messages at every time step** - ✓ Tracked and counted separately
5. **Dynamic scenarios with probabilities** - ✓ p_request, p_fail, p_new parameters
6. **Message counting system** - ✓ Hello, topology, route discovery, data packets
7. **Protocol efficiency calculation** - ✓ Efficiency = data_packets / total_packets

### 📊 **Protocol Efficiency Breakdown:**
```
Typical efficiency ranges:
- Static networks: 8-15% (good performance)
- Light dynamics: 5-10% (acceptable performance)  
- Heavy dynamics: 2-5% (realistic mobile networks)
- Research evaluation: 3-7% (multi-topology average)
```

## 🔧 Command-Line Reference

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--nodes=<N>` | Number of nodes in network | 15 | `--nodes=10` |
| `--dynamic` | Enable dynamic topology changes | False | `--dynamic` |
| `--time-steps=<N>` | Number of simulation time steps | 20 | `--time-steps=30` |
| `--p-request=<0-1>` | Probability of packet request per step | 0.3 | `--p-request=0.5` |
| `--p-fail=<0-1>` | Probability of link failure per step | 0.1 | `--p-fail=0.2` |
| `--p-new=<0-1>` | Probability of new link per step | 0.1 | `--p-new=0.15` |
| `--evaluation` | Run research evaluation mode | False | `--evaluation` |
| `--topologies=<N>` | Number of topologies to evaluate | 5 | `--topologies=3` |
| `--iterations=<N>` | Iterations per topology | 10 | `--iterations=20` |
| `--interactive` | Show real-time visualizations | False | `--interactive` |

## 🔬 Understanding the Results

### **Message Types Explained:**
- **Hello Messages**: Neighbor awareness (required by academic standard)
- **Topology Messages**: Initial network discovery 
- **Route Discovery**: Protocol convergence and updates
- **Data Packets**: Actual payload transmission

### **Efficiency Interpretation:**
- **8%+ efficiency**: Excellent performance, minimal overhead
- **5-8% efficiency**: Good performance, acceptable overhead
- **2-5% efficiency**: Realistic mobile network performance
- **<2% efficiency**: Heavy dynamics, high protocol overhead

### **Network Metrics:**
- **Convergence**: Usually 2-3 iterations for small networks
- **Reachability**: Percentage of nodes that can communicate
- **Average delay**: End-to-end transmission time
- **Success rate**: Percentage of successful transmissions

## 🧪 Testing & Validation

```bash
# Run all tests
python tests/test_suite.py

# Simple functionality test
python tests/test_simple.py

# Performance testing
python tests/test_iterations.py
```

**Expected test results:** 10/10 tests passing ✅

## 📂 Project Structure

```
wireless-network/
├── src/
│   ├── core/                 # Core simulation engine
│   │   ├── network.py        # Distance vector protocol
│   │   ├── sensor_node.py    # Node implementation
│   │   └── evaluation.py     # Research evaluation
│   ├── visualization/        # Network visualization
│   └── reporting/           # Report generation
├── tests/                   # Test suites
├── output/
│   ├── reports/            # Generated reports
│   └── visualizations/     # Network graphs
└── simulation.py           # Main entry point
```

## 🎓 Academic Use Cases

### **Protocol Research:**
```bash
# Compare different network sizes
python simulation.py --evaluation --nodes=10
python simulation.py --evaluation --nodes=20

# Study network dynamics
python simulation.py --dynamic --p-fail=0.1 --time-steps=50

# Efficiency analysis
python simulation.py --evaluation --topologies=20 --iterations=50
```

### **Network Design:**
```bash
# Test network resilience
python simulation.py --dynamic --p-fail=0.3 --p-new=0.1

# Optimize for efficiency
python simulation.py --p-request=0.8 --nodes=5

# Study topology effects
python simulation.py --evaluation --max-prob=0.5
```

## 📈 Performance Expectations

### **Computational Performance:**
- 5 nodes: ~0.1 seconds
- 15 nodes: ~0.5 seconds  
- 50 nodes: ~3 seconds
- Evaluation mode: 2-10 seconds depending on parameters

### **Memory Usage:**
- Minimal memory footprint
- Scales linearly with network size
- Suitable for networks up to 100+ nodes

## 🔧 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python tests/test_simple.py
```

**Requirements:**
- Python 3.7+
- NetworkX, Matplotlib, NumPy
- Standard libraries: random, math, logging

## 💡 Research Applications

This simulator is designed for:
- **Protocol evaluation** studies
- **Network topology** research  
- **Dynamic network** behavior analysis
- **Routing efficiency** measurements
- **Academic coursework** in networking

## 🎯 Key Academic Features

1. **Deterministic seed support** for reproducible results
2. **Comprehensive message tracking** for protocol analysis  
3. **Multiple evaluation metrics** for research comparison
4. **Academic-standard efficiency calculation**
5. **Research-quality report generation**
6. **Standards-compliant hello message implementation**

---

📧 **For academic use, research questions, or contributions, see the project repository.**
