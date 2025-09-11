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
- Hello Messages: 52 (35.4%) - neighbor discovery
- Topology Messages: 36 (24.5%) - route updates  
- Route Discovery: 45 (30.6%) - initial convergence
- Data Packets: 14 (9.5%) - actual payload
Protocol Efficiency: 9.52%
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

### 3. � **Evaluation Mode** - Research Analysis
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
Topology 1: 3.50% efficiency (200 total packets)
Topology 2: 4.12% efficiency (185 total packets)
Topology 3: 2.87% efficiency (210 total packets)
Overall average: 3.50% efficiency
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

# Test basic protocol efficiency
python simulation.py --nodes=5
```

### Dynamic Network Testing  
```bash
# High activity network (more events)
python simulation.py --dynamic --p-request=0.8 --time-steps=10

# Low activity network (stable)
python simulation.py --dynamic --p-request=0.1 --p-fail=0.05
```

### Research Analysis
```bash
# Quick evaluation (3 topologies, 2 iterations each)
python simulation.py --evaluation --topologies=3 --iterations=2

# Comprehensive evaluation (10 topologies, 10 iterations each)  
python simulation.py --evaluation --topologies=10 --iterations=10
```

## 📊 Understanding Protocol Efficiency

**What is Protocol Efficiency?**
```
Efficiency = Data Packets / Total Packets
```

**Message Types Tracked:**
1. **Hello Messages** - Neighbor discovery (sent regularly)
2. **Topology Messages** - Distance vector updates  
3. **Route Discovery** - Path establishment
4. **Data Packets** - Actual payload transmission

**Typical Efficiency Ranges:**
- **5-15%**: Normal for research protocols with hello messages
- **20-30%**: Good efficiency (optimized parameters)
- **<5%**: High control overhead (frequent topology changes)

## ⚙️ Command-Line Options Reference

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--nodes=N` | Network size (number of nodes) | 15 | `--nodes=25` |
| `--dynamic` | Enable topology changes over time | Off | `--dynamic` |
| `--time-steps=N` | Duration of dynamic simulation | 20 | `--time-steps=50` |
| `--p-request=X` | Data request probability (0.0-1.0) | 0.3 | `--p-request=0.7` |
| `--p-fail=X` | Link failure probability (0.0-1.0) | 0.1 | `--p-fail=0.05` |
| `--p-new=X` | New link probability (0.0-1.0) | 0.1 | `--p-new=0.15` |
| `--evaluation` | Run research analysis mode | Off | `--evaluation` |
| `--topologies=N` | Number of networks to test | 5 | `--topologies=10` |
| `--iterations=N` | Tests per topology | 10 | `--iterations=20` |
| `--interactive` | Show visual network graphs | Off | `--interactive` |

## 🔬 Protocol Implementation Details

### Distance Vector Routing Protocol
- **Hello Messages**: Sent every iteration to discover and maintain neighbors
- **Convergence**: Protocol finds shortest paths using distributed Bellman-Ford
- **Dynamic Adaptation**: Automatically reconverges when topology changes
- **Link Weights**: All delays constrained to 0.0-1.0 second range

### Key Requirements Implemented
✅ **Proactive routing** - Distance vector with hello messages  
✅ **Dynamic topology** - Links can fail and appear during simulation  
✅ **Message counting** - All packet types tracked separately  
✅ **Protocol efficiency** - Data packets vs total packets ratio  
✅ **Delay constraints** - All link delays between 0.0-1.0 seconds  
✅ **Academic compliance** - Follows networking research standards

## � Output Files Generated

After running simulations, check these directories:

**Reports:**
- `output/reports/network_report.txt` - Basic simulation results
- `output/reports/evaluation_report.txt` - Multi-topology analysis

**Visualizations:**
- `output/visualizations/network_visualization_*.png` - Network graphs
- `output/visualizations/network_adjacency_list.png` - Connection diagrams

## 🧪 Installation & Testing

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python tests/test_simple.py
```

### Run Test Suite
```bash
# Basic functionality tests
python tests/test_simulator.py

# Full test suite
python tests/test_suite.py
```

## 🎯 Example Usage Scenarios

### Academic Research
```bash
# Generate data for research paper
python simulation.py --evaluation --topologies=20 --iterations=50
```

### Protocol Debugging
```bash
# Small network with visualization
python simulation.py --nodes=5 --interactive
```

### Stress Testing
```bash
# High-churn dynamic network
python simulation.py --dynamic --p-fail=0.3 --p-new=0.3 --time-steps=30
```

### Performance Optimization
```bash
# Test different parameters
python simulation.py --dynamic --p-request=0.8 --p-fail=0.01
```

---

## � Tips for New Users

1. **Start Simple**: Run `python simulation.py` first to see basic operation
2. **Use Interactive Mode**: Add `--interactive` to see what's happening visually  
3. **Check Outputs**: Look in `output/reports/` for detailed results
4. **Small Networks**: Use `--nodes=5` for faster testing and debugging
5. **Academic Use**: Use `--evaluation` mode for research and comparative analysis

**Need help?** All simulation modes generate detailed console output explaining what's happening step-by-step.

### Dynamic Simulation
- **`--dynamic`**: Enables dynamic network behavior where topology changes over time.
- **`--time-steps=<number>`**: Number of discrete time periods in the simulation.
- **`--p-request=<float>`**: Controls how often data transmission requests are generated (0-1).
- **`--p-fail=<float>`**: Controls how often existing links fail (0-1).
- **`--p-new=<float>`**: Controls how often new links form between nodes (0-1).
- **`--delay=<float>`**: Controls the real-time delay between simulation steps.
- **`--hello-interval=<number>`**: Controls hello message frequency (0=never, 1=every step, N=every N steps).

### Protocol Efficiency Control
- **`--ignore-initial-route-discovery`**: (Default) Reset route discovery counters after initial convergence for static networks. Provides operational efficiency measurements.
- **`--consider-initial-route-discovery`**: Include all route discovery messages in efficiency calculations. Provides total protocol cost measurements including startup overhead.

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

## 🎯 Performance Optimization & Best Practices

### Achieving High Efficiency

**For Static Networks (90%+ efficiency):**
```bash
# Optimal static network configuration
python simulation.py --dynamic --p-fail=0.0 --p-new=0.0 --hello-interval=0 --p-request=0.8
```

**For Dynamic Networks (20-60% efficiency):**
```bash
# Low churn network (good efficiency)
python simulation.py --dynamic --p-fail=0.001 --p-new=0.001 --hello-interval=20

# Moderate churn network (acceptable efficiency) 
python simulation.py --dynamic --p-fail=0.01 --p-new=0.01 --hello-interval=10

# High churn network (low efficiency, realistic for mobile networks)
python simulation.py --dynamic --p-fail=0.05 --p-new=0.05 --hello-interval=5
```

### Parameter Guidelines

**Topology Change Probabilities:**
- `p_fail, p_new < 0.001`: Minimal impact on efficiency (~80-90%)
- `p_fail, p_new = 0.01`: Moderate impact (~20-40% efficiency)  
- `p_fail, p_new > 0.05`: High impact (<20% efficiency)

**Hello Interval Optimization:**
- Static networks: Use `--hello-interval=0` (no hello messages needed)
- Low-churn networks: Use `--hello-interval=50` or higher
- High-churn networks: Use `--hello-interval=5-10` for fast failure detection

**Request Probability:**
- Higher `p_request` values improve efficiency by increasing data traffic ratio
- Recommended range: 0.3-0.8 depending on application requirements

### Interpreting Efficiency Results

**Efficiency Categories:**
- **90%+**: Excellent (typical for static networks with optimized parameters)
- **60-90%**: Good (low-churn networks with reasonable hello intervals)
- **30-60%**: Acceptable (moderate churn or frequent hello messages)
- **10-30%**: Poor (high churn networks, may need protocol optimization)
- **<10%**: Critical (network spending most bandwidth on control traffic)

**Common Efficiency Issues:**
- High route discovery percentage: Reduce p_fail/p_new or increase convergence speed
- High hello message percentage: Increase hello-interval or disable in static networks
- Low data packet percentage: Increase p_request or reduce control overhead

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

## 🔮 Future Enhancements

### Recently Added Features ✅
- **Protocol Efficiency Analysis**: Detailed breakdown of message types and efficiency metrics
- **Initial Route Discovery Control**: Options to include/exclude startup costs in efficiency calculations  
- **Hello Message Configuration**: Configurable hello message intervals for different network scenarios
- **Static Network Optimization**: Automatic detection and optimization for static network scenarios

### Planned Enhancements 🚧
1. **Advanced Routing Protocols**: AODV, DSR, OLSR, and other modern routing protocols
2. **Energy Modeling**: Battery consumption simulation and energy-aware routing algorithms
3. **Mobile Nodes**: Support for nodes that change position over time with mobility models
4. **Interference Modeling**: RF signal interference and collision detection
5. **Quality of Service**: Priority-based routing and bandwidth allocation
6. **Security Features**: Authentication, encryption, and intrusion detection
7. **3D Visualization**: Support for 3D networks with terrain and obstacle modeling
8. **Real-time Mode**: Live network monitoring and control capabilities

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
