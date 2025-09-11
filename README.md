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

### Node Configuration
- **`--nodes=<number>`**: Controls the size of the network. More nodes create a denser network with more potential paths but increase simulation complexity.

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
