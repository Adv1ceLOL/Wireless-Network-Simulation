# 🌐 Wireless Sensor Network Simulator

A comprehensive simulator for wireless sensor networks implementing proactive distance vector routing protocol. This simulator models dynamic network topology changes, message transmission, and protocol efficiency according to academic networking research standards.

## 🚀 Command-Line Options

```
python simulation.py [options]
```

| Option                | Description                                         | Default    |
|-----------------------|-----------------------------------------------------|------------|
| `--interactive`, `-i` | Enable interactive visualizations                   | False      |
| `--nodes=<number>`    | Set the number of nodes in the network              | 15         |
| `--dynamic`           | Run dynamic scenario simulation                     | False      |
| `--time-steps=<number>` | Number of time steps for dynamic scenario         | 20         |
| `--p-request=<float>` | Probability of packet request per time step         | 0.3        |
| `--p-fail=<float>`    | Probability of link failure per time step           | 0.1        |
| `--p-new=<float>`     | Probability of new link formation per time step     | 0.1        |
| `--delay=<float>`     | Delay between time steps in seconds                 | 1.0        |
| `--evaluation`, `-e`  | Run protocol evaluation mode                         | False      |
| `--topologies=<number>` | Number of topologies to evaluate in evaluation mode  | 5          |
| `--iterations=<number>` | Iterations per topology in evaluation mode           | 10         |
| `--max-prob=<float>`  | Max probability for parameters in evaluation mode    | 0.3        |

## 📂 Directory Structure

```
wireless-network/
├── src/                  # Core source code
│   ├── core/             # Core simulator functionality
│   ├── visualization/    # Visualization modules
│   └── reporting/        # Reporting and analysis tools
├── tests/                # Test cases and test suites
├── docs/                 # Documentation
├── output/               # Generated files
│   ├── visualizations/   # Network visualizations
│   └── reports/          # Network reports
└── simulation.py         # Main entry point
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
