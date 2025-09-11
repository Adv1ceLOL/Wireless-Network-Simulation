# 🌐 Wireless Sensor Network Simulator

A comprehensive simulator for wireless sensor networks implementing proactive distance vector routing protocol. This simulator models dynamic network topology changes, message transmission, and protocol efficiency according to academic networking research standards.

## 🎯 What This Simulator Does

This simulator implements the requirements from academic research for wireless sensor networks:
- **Proactive Distance Vector Routing**: Uses distributed Bellman-Ford algorithm for optimal path discovery
- **Dynamic Network Topology**: Simulates real-world link failures and new connections
- **Hello Message Protocol**: Nodes exchange hello messages with neighbors for network discovery
- **Protocol Efficiency Analysis**: Measures data packet ratio vs. control message overhead
- **Weighted Link Delays**: Random delays between 0-1 seconds representing realistic network conditions

## 🚀 Simulation Modes

### 1. 📊 **Default Mode** - Static Network Analysis
```bash
python simulation.py
```
**What it does:**
- Creates a fixed network topology with N nodes (default: 15)
- Runs proactive distance vector protocol for route discovery
- Sends hello messages between neighbors
- Simulates random message transmissions
- Measures protocol efficiency (typically 8-12%)

**Example Output:**
```
Network created with 15 nodes
Hello Messages: 84 (35.2%)
Data Packets: 12 (5.0%)
Protocol Efficiency: 8.22%
Success Rate: 100%
```

### 2. ⚡ **Dynamic Mode** - Real-World Network Simulation
```bash
python simulation.py --dynamic
```
**What it does:**
- Simulates network over multiple time steps (default: 20)
- **Every time step:** Nodes exchange hello messages
- **Random events:** Link failures (p_fail=0.1), new links (p_new=0.1), packet requests (p_request=0.3)
- **Protocol adaptation:** Network reconverges after topology changes

**Example Output:**
```
Time Step 5/20:
- Hello messages exchanged: 45
- Link failure: Node 3-7 disconnected
- Protocol reconverged in 3 iterations
- New packet request: Node 2 → Node 8 (SUCCESS)
```

### 3. 🔬 **Evaluation Mode** - Protocol Performance Analysis
```bash
python simulation.py --evaluation
```
**What it does:**
- Tests protocol across multiple random topologies
- Varies parameters (p_request, p_fail, p_new) to stress-test the network
- Generates comprehensive efficiency reports
- Compares network performance metrics

**Example Output:**
```
PROTOCOL EVALUATION REPORT
Topologies tested: 5
Average efficiency: 2.5%
Best topology efficiency: 4.8%
Network resilience score: 8.2/10
```

### 4. 🎨 **Interactive Mode** - Visual Network Exploration
```bash
python simulation.py --interactive
```
**What it does:**
- All features of default mode PLUS interactive network visualizations
- Real-time network topology graphs
- Visual routing table displays

## 📋 Command-Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--nodes=<N>` | Number of network nodes | 15 | `--nodes=25` |
| `--dynamic` | Enable dynamic topology changes | False | `--dynamic` |
| `--time-steps=<N>` | Steps for dynamic simulation | 20 | `--time-steps=50` |
| `--p-request=<0-1>` | Probability of packet request per step | 0.3 | `--p-request=0.7` |
| `--p-fail=<0-1>` | Probability of link failure per step | 0.1 | `--p-fail=0.05` |
| `--p-new=<0-1>` | Probability of new link per step | 0.1 | `--p-new=0.15` |
| `--evaluation` | Run protocol evaluation analysis | False | `--evaluation` |
| `--topologies=<N>` | Number of topologies to evaluate | 5 | `--topologies=10` |
| `--iterations=<N>` | Iterations per topology | 10 | `--iterations=20` |
| `--interactive` | Enable visual network displays | False | `--interactive` |

## 🔬 Understanding the Protocol

### Distance Vector Routing
- **Initialization**: Each node knows only its direct neighbors
- **Convergence**: Nodes exchange routing information until network-wide optimal paths are found
- **Adaptation**: When topology changes, protocol automatically reconverges

### Message Types Tracked
1. **Hello Messages**: Neighbor discovery and maintenance
2. **Topology Messages**: Distance vector exchanges for route discovery  
3. **Route Discovery**: Control packets for path establishment
4. **Data Packets**: Actual payload transmissions

### Protocol Efficiency Formula
```
Efficiency = Data Packets / Total Packets
```
- **Higher efficiency** = More data, less control overhead
- **Typical range**: 5-15% (academic networking standards)

## 📊 What to Expect

### Default Mode Results
```
Message Exchange Analysis:
Hello Messages: 84 (35.2%)
Topology Messages: 36 (15.1%) 
Route Discovery: 105 (44.0%)
Data Packets: 14 (5.9%)
Protocol Efficiency: 5.86%
```

### Dynamic Mode Results
```
Dynamic Scenario Summary:
Time steps completed: 20
Link failures: 3
New links added: 2
Successful transmissions: 18/22
Network adaptation time: avg 2.1 iterations
```

### Evaluation Mode Results
```
Topology Performance Comparison:
Best network efficiency: 4.8%
Network resilience: 85%
Average convergence: 2.3 iterations
Recommendation: Topology 3 (score: 8.7/10)
```

## 💻 Quick Start Examples

### Test Basic Protocol
```bash
# Simple 10-node network
python simulation.py --nodes=10
```

### Stress Test Network
```bash
# High-activity dynamic scenario  
python simulation.py --dynamic --p-request=0.8 --p-fail=0.2 --time-steps=30
```

### Research Analysis
```bash
# Comprehensive protocol evaluation
python simulation.py --evaluation --topologies=10 --iterations=50
```

## 📁 Output Files

The simulator generates:
- **Network Reports**: `output/reports/network_report.txt`
- **Evaluation Analysis**: `output/reports/evaluation_report.txt`  
- **Network Visualizations**: `output/visualizations/network_*.png`

## 🧪 Academic Compliance

This simulator implements all requirements from networking research standards:
- ✅ Proactive routing protocol (Distance Vector)
- ✅ Dynamic topology changes (link failures/additions)
- ✅ Hello message exchanges
- ✅ Weighted links (0-1 second delays)
- ✅ Protocol efficiency measurement
- ✅ Message counting (all types)
- ✅ Parameter variation analysis

### Dynamic Simulation
- **`--dynamic`**: Enables dynamic network behavior where topology changes over time.
- **`--time-steps=<number>`**: Number of discrete time periods in the simulation.
- **`--p-request=<float>`**: Controls how often data transmission requests are generated (0-1).
- **`--p-fail=<float>`**: Controls how often existing links fail (0-1).
- **`--p-new=<float>`**: Controls how often new links form between nodes (0-1).
- **`--delay=<float>`**: Controls the real-time delay between simulation steps.

### Protocol Evaluation
- **`--evaluation`, `-e`**: Enables protocol evaluation mode that compares multiple network topologies.
- **`--topologies=<number>`**: Number of random network topologies to generate and evaluate.
- **`--iterations=<number>`**: Number of simulation iterations to run per topology with different parameters.
- **`--max-prob=<float>`**: Maximum probability value for randomized parameters (p_fail and p_new).

### Visualization
- **`--interactive`**: Shows network topology and changes in real-time using matplotlib.

## ⚙️ Installation

```bash
# Install Python packages
pip install -r requirements.txt

# Run a simple test script to check everything is ok
python tests/test_simple.py
```

## 🧪 Testing

The project includes several test suites to verify functionality:

```bash
# Run simple tests
python tests/test_simple.py

# Run comprehensive tests
python tests/test_simulator.py

# Run performance tests with multiple iterations
python tests/test_iterations.py [num_iterations]

# Run the full test suite
python tests/test_suite.py
```

## 📊 Visualization

The simulator supports multiple visualization methods:

1. **Matplotlib**: Basic network visualization with nodes and connections
2. **NetworkX**: Graph-based visualization with network metrics
3. **Adjacency List**: Text-based representation of network connections

All visualizations are saved to the `output/visualizations/` directory.

## 🔧 Troubleshooting

### Visualization Issues

If you encounter problems with interactive visualization:

1. **Missing GUI Backend**: 
   ```bash
   # Windows
   pip install tk
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install python3-tk
   
   # macOS
   pip install PyQt5
   ```

2. **No Visualizations Generated**:
   - Make sure you have at least one of: matplotlib, networkx, or PIL/Pillow installed

### Cross-Platform Issues

- **Windows**: Use semicolons instead of && for command chaining in PowerShell
- **Linux**: Install tkinter with `sudo apt-get install python3-tk` (Debian/Ubuntu)
- **macOS**: Try PyQt5 as an alternative: `pip install PyQt5`

## � Protocol Evaluation

The simulator includes a comprehensive protocol evaluation mode that analyzes network performance across multiple topologies:

### Scoring Metrics

Each topology is scored based on the following weighted metrics:

- **Efficiency (25%)**: Ratio of data packets to total packets
- **Resilience (20%)**: Network ability to handle topology changes and maintain connectivity
- **Overhead (15%)**: Efficiency of control message usage
- **Routing Quality (20%)**: Quality of routing paths based on average hop count (fewer is better)
- **Delay Factor (10%)**: Quality of paths based on link weights/delays (lower is better)
- **Traffic Balance (10%)**: Balance between data volume and network capacity

### Evaluation Reports

The evaluation mode generates detailed reports in the `output/reports/` directory:
- Topology-by-topology statistics
- Comparative analysis across topologies
- Detailed scoring breakdowns
- Cross-topology metric comparisons

### Running an Evaluation

```bash
# Basic evaluation with default parameters
python simulation.py --evaluation

# Advanced evaluation with custom parameters
python simulation.py --evaluation --topologies=10 --iterations=20 --max-prob=0.5
```

## �🔮 Future Enhancements

1. **Advanced Routing Protocols**: AODV, DSR, and other routing protocols
2. **Energy Modeling**: Battery consumption simulation and energy-aware routing
3. **Mobile Nodes**: Support for nodes that change position over time
4. **Interference Modeling**: Signal interference simulation
5. **3D Visualization**: Support for 3D networks with terrain effects

## 👥 Contributing

Contributions are welcome! Here are some ways you can contribute:
1. Report bugs and issues
2. Add new features or enhancements
3. Improve documentation
4. Add more test cases

## 🙏 Acknowledgments

- Based on the Internet Of Things course at Sapienza Universita di Roma
- Special thanks to Marismar da Costa Silva and Gustavo Eraldo da Silva for code structure ideas for the Random generation of the topology.


Changes:

Based on your request to improve efficiency while maintaining the requirements from request.txt, I've analyzed the codebase and identified the key issues and opportunities for improvement. Here's what I found:

Current Efficiency Problems
Looking at your evaluation results showing only 1.37% efficiency (69 data packets out of 5,044 total), the main issues are:

1. Excessive Hello Message Frequency
Current Problem: Hello messages are sent every time step to every neighbor

This generates 48.22% of all traffic (2,432 messages).

2. Excessive Route Discovery Overhead
Current Problem: Route discovery happens too frequently

45.26% of traffic (2,283 messages)
Should only happen during initial setup and after topology changes
3. Low Data Transmission Rate
With p_request=0.75 over 100 time steps, you should get ~75 data requests, but only got 69.

Solutions to Improve Efficiency
1. Optimize Hello Message Frequency
File: src/core/evaluation.py (lines 158-164)

Current Code:

Improved Solution:

2. Reduce Route Discovery Overhead
File: src/core/network.py (lines 386+)

Current Issue: Route discovery messages are being overcounted

Solution: Implement incremental route updates instead of full table exchanges:

3. Implement Adaptive Hello Intervals
New Parameter System:

4. Optimize Data Packet Requests
File: src/core/evaluation.py (lines 170-185)
