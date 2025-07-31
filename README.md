# 🌐 Wireless Sensor Network Simulator

A robust simulator for wireless sensor networks that models node connectivity, data transmission, and routing protocols with interactive visualization capabilities.

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
| `--hello-interval=<number>` | Send hello messages every N time steps (0=never) | 1          |
| `--ignore-initial-route-discovery` | Reset route discovery counters after convergence | True |
| `--consider-initial-route-discovery` | Include initial route discovery in efficiency | False |
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

## 💻 Usage Examples

### Basic Simulation
```bash
python simulation.py
```

### Interactive Visualization
```bash
python simulation.py --interactive
```

### Dynamic Scenario
```bash
python simulation.py --dynamic --nodes=10 --time-steps=5 --p-request=0.5 --p-fail=0.2 --p-new=0.3
```

### Protocol Efficiency Control
```bash
# Default behavior - ignore initial route discovery (recommended for static networks)
python simulation.py --dynamic --nodes=50 --time-steps=100 --p-fail=0.0 --p-new=0.0

# Include initial route discovery messages in efficiency calculations
python simulation.py --dynamic --nodes=50 --time-steps=100 --p-fail=0.0 --p-new=0.0 --consider-initial-route-discovery

# Custom hello message intervals
python simulation.py --dynamic --hello-interval=10  # Send hello every 10 steps
python simulation.py --dynamic --hello-interval=0   # Never send hello messages
```

### Static vs Dynamic Network Analysis
```bash
# High efficiency static network (no topology changes)
python simulation.py --dynamic --p-fail=0.0 --p-new=0.0 --p-request=0.5

# Dynamic network with moderate changes
python simulation.py --dynamic --p-fail=0.01 --p-new=0.01 --p-request=0.3

# High churn network (efficiency will be low due to overhead)
python simulation.py --dynamic --p-fail=0.1 --p-new=0.1 --p-request=0.3
```

### Protocol Evaluation Mode
```bash
python simulation.py --evaluation --topologies=3 --iterations=5 --max-prob=0.4
```

### Windows PowerShell Users
In PowerShell, use semicolons instead of `&&` for command chaining:
```powershell
python simulation.py --nodes=20; python simulation.py --interactive
```

## 🔍 Understanding Command-Line Options

## 📊 Protocol Efficiency Analysis

The simulator provides detailed protocol efficiency analysis that measures how much of the network traffic consists of useful data packets versus protocol overhead. Understanding these metrics is crucial for evaluating network performance.

### Efficiency Metrics

The simulator tracks four types of network messages:

1. **Data Packets**: Actual user data being transmitted between nodes
2. **Hello Messages**: Periodic neighbor discovery messages  
3. **Topology Messages**: Initial network topology discovery messages
4. **Route Discovery**: Distance vector protocol routing table updates

**Protocol Efficiency = Data Packets / Total Messages**

### Key Insights

#### Static Networks (p_fail=0.0, p_new=0.0)
- **Expected Efficiency**: 80-95% with proper configuration
- **Overhead Sources**: Initial topology discovery, hello messages
- **Recommendation**: Use `--ignore-initial-route-discovery` (default) for realistic operational efficiency

#### Dynamic Networks (p_fail>0.01 or p_new>0.01)  
- **Expected Efficiency**: 5-30% depending on change frequency
- **Overhead Sources**: Route discovery due to topology changes, hello messages, topology updates
- **Critical Threshold**: Networks with p_fail or p_new > 0.01 experience significant efficiency degradation

#### The 0.01 Threshold Effect
Probability values above ~0.01 for topology changes cause dramatic efficiency drops:
- **p_fail=0.001**: ~70% efficiency 
- **p_fail=0.01**: ~25% efficiency
- **p_fail=0.1**: ~5% efficiency

This occurs because frequent topology changes trigger continuous route discovery updates, overwhelming the network with control traffic.

### Route Discovery Counting Options

The simulator provides two approaches for measuring efficiency:

#### `--ignore-initial-route-discovery` (Default: True)
- **Purpose**: Measures operational efficiency after network convergence
- **Use Case**: Evaluating steady-state network performance
- **Method**: Resets route discovery counters after initial protocol convergence in static networks
- **Result**: Higher efficiency values reflecting actual operational performance

#### `--consider-initial-route-discovery`
- **Purpose**: Measures total protocol cost including network setup
- **Use Case**: Evaluating complete protocol overhead from startup
- **Method**: Includes all route discovery messages from simulation start
- **Result**: Lower efficiency values including initialization costs

### Choosing the Right Measurement

**Use `--ignore-initial-route-discovery` (default) when:**
- Evaluating long-running network performance
- Comparing operational efficiency between protocols
- Analyzing steady-state behavior
- The network topology is relatively stable

**Use `--consider-initial-route-discovery` when:**
- Measuring total protocol cost for short-lived networks
- Evaluating startup overhead impact
- Analyzing protocols where initialization cost matters
- Comparing different convergence algorithms

### Hello Message Configuration

The `--hello-interval` parameter controls neighbor discovery frequency:
- `--hello-interval=0`: No hello messages (assumes pre-established topology)
- `--hello-interval=1`: Hello every time step (maximum overhead)
- `--hello-interval=10`: Hello every 10 steps (balanced approach)

Higher hello frequencies improve fault detection but reduce efficiency.

## 🔍 Understanding Command-Line Options

### Node Configuration
- **`--nodes=<number>`**: Controls the size of the network. More nodes create a denser network with more potential paths but increase simulation complexity.

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
