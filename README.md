# Wireless Sensor Network Simulator

A robust simulator for wireless sensor networks that models node connectivity, data transmission, and routing protocols with interactive visualization capabilities.

## Project Structure

The project is organized into the following directories:

- `src/`: Core source code
  - `core/`: Core simulator functionality
  - `visualization/`: Visualization modules
  - `reporting/`: Reporting and analysis tools
- `scripts/`: Setup and utility scripts
- `tests/`: Test cases and test suites
- `docs/`: Documentation
- `output/`: Generated files
  - `visualizations/`: Network visualizations
  - `reports/`: Network reports

## Installation

### Automatic Installation

The easiest way to install all dependencies is to use the automatic installer:

**Windows:**
```
scripts\setup_windows.bat
```

**Unix (Linux/macOS):**
```bash
chmod +x scripts/setup_unix.sh
scripts/setup_unix.sh
```

### Manual Installation

To manually install the required dependencies:

```bash
# Install Python packages
pip install matplotlib networkx pillow

# Run dependency check
python scripts/install_dependencies.py
```

## Usage

### Basic Usage

To run the simulator with default settings:

```bash
python simulation.py
```

### Interactive Mode

To run the simulator with interactive visualizations:

```bash
python simulation.py --interactive
```

In interactive mode, visualization windows will appear and stay open until you press Enter.

### Custom Network Configuration

To specify custom network parameters:

```bash
python simulation.py --nodes 15 --area 20 --min-range 2.0 --max-range 4.0
```

### Other Options

```bash
# Run with verbose output
python simulation.py --verbose

# Generate detailed report
python simulation.py --detailed-report

# Help and options
python simulation.py --help
```

### Dynamic Scenario Simulation

Run a dynamic scenario simulation where link failures, new connections, and packet requests occur probabilistically at each time step:

```bash
python simulation.py --dynamic --nodes=8 --time-steps=5 --p-request=0.6 --p-fail=0.2 --p-new=0.3 --interactive
```

This example runs a dynamic simulation with:
- 8 nodes in the network
- 5 time steps (iterations)
- 60% probability of packet requests at each step
- 20% probability of link failures at each step
- 30% probability of new link formations at each step
- Interactive mode to visualize network changes

Dynamic scenarios are useful for testing network robustness, routing protocol convergence, and adaptive behavior in changing conditions. The simulator tracks statistics like message delivery success rate, average delay, and network topology changes.

## Testing

The project includes several test suites:

```bash
# Run simple tests
python tests/test_simple.py

# Run comprehensive tests
python tests/test_simulator.py

# Run performance tests with multiple iterations
python tests/test_iterations.py [num_iterations]
```

## Visualization

The simulator supports multiple visualization methods:

1. **Matplotlib**: Basic network visualization with nodes and connections
2. **NetworkX**: Graph-based visualization with network metrics
3. **Adjacency List**: Text-based representation of network connections

## Core Components

### SensorNode

The `SensorNode` class represents a wireless sensor node with:
- Spatial coordinates
- Transmission range
- Connection list
- Routing table

### SensorNetwork

The `SensorNetwork` class manages:
- Node creation and connection establishment
- Distance vector routing protocol
- Message transmission simulation
- Network analytics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

For interactive visualizations, you'll also need a GUI backend:

- **Windows**: `tkinter` (included with Python)
- **macOS**: `pip install PyQt5`
- **Linux**: `sudo apt-get install python3-tk` (Debian/Ubuntu) or `pip install PyQt5`

## Usage

### Basic Simulation

Run a basic simulation with default parameters:

```bash
python simulation.py
```

### Interactive Visualization

Run with interactive visualization enabled:

```bash
python simulation.py --interactive
```

### Customizing Simulation Parameters

Specify the number of nodes:

```bash
python simulation.py --nodes=20
```

Run with both interactive mode and custom parameters:

```bash
python simulation.py --nodes=20 --interactive
```

### Windows PowerShell Users

In PowerShell, use semicolons instead of `&&` for command chaining:

```powershell
python simulation.py --nodes=20; python simulation.py --interactive
```

## Testing

To test the functionality:

```bash
python test_simple.py
```

To run multiple iterations with different parameters:

```bash
python test_iterations.py [number_of_iterations]
```

For running the full test suite:

```bash
python tests/test_suite.py
```

## Visualization Examples

The simulator generates three types of visualizations:

1. **Physical Network Topology (Matplotlib)**
   - Shows nodes with their physical positions
   - Displays transmission range circles
   - Connections are color-coded by delay (green = low delay, red = high delay)

2. **Graph Visualization (NetworkX)**
   - Displays the network as a graph
   - Nodes positioned according to their physical coordinates
   - Edges have varying thickness and color based on delay
   - Includes a color legend for reference

3. **Adjacency List Representation**
   - Text-based representation of network connections
   - Lists each node's neighbors with delay values
   - Easy to read, consistent format

All visualizations are saved to the `visualizations` directory by default.

## Troubleshooting

### Visualization Issues

If you encounter problems with interactive visualization:

1. **Missing GUI Backend**: 
   - Error: "No interactive backends available" or "No GUI backend found"
   - Solution: Install a GUI backend for matplotlib based on your operating system:
     ```bash
     # Windows (in Command Prompt or PowerShell)
     pip install tk
     
     # Linux (Ubuntu/Debian)
     sudo apt-get install python3-tk
     
     # macOS
     pip install PyQt5  # Alternative to Tk
     ```

2. **Backend Crashes**:
   - If the default backend crashes, the simulator will try others automatically
   - You can also try installing alternative backends:
     ```bash
     pip install PyQt5 wxPython
     ```

3. **No Visualizations Generated**:
   - If no visualizations are generated, the simulator will fall back to simple visualization using PIL
   - Make sure you have at least one of the following installed: matplotlib, networkx, or PIL/Pillow

### Cross-Platform Issues

1. **Windows**:
   - If you're using PowerShell, use semicolons instead of && for command chaining
   - Tkinter should be included with standard Python installations
   - For conda environments, you may need to install tk separately

2. **Linux**:
   - Tkinter is typically not included by default
   - Install with: `sudo apt-get install python3-tk` (Debian/Ubuntu)
   - For other distributions, use the appropriate package manager

3. **macOS**:
   - Tkinter may have issues on some macOS versions
   - PyQt5 is a good alternative: `pip install PyQt5`
   - If using Homebrew Python, you may need additional steps

## Future Enhancements

Potential improvements for future versions:

1. **Advanced Routing Protocols**:
   - Add support for AODV, DSR, and other routing protocols
   - Compare performance between different routing strategies

2. **Energy Modeling**:
   - Simulate battery consumption for transmission and reception
   - Implement energy-aware routing protocols

3. **Mobile Nodes**:
   - Add support for nodes that change position over time
   - Implement mobility models (random walk, random waypoint, etc.)

4. **Interference Modeling**:
   - Simulate signal interference between nodes
   - More realistic communication modeling

5. **3D Visualization**:
   - Support for 3D networks and terrain effects
   - Interactive 3D visualization

## Contributing

Contributions are welcome! Here are some ways you can contribute:

1. Report bugs and issues
2. Add new features or enhancements
3. Improve documentation
4. Add more test cases


## Acknowledgments

- Based on the wireless networks course at UFPB
- Special thanks to the original authors: Marismar da Costa Silva and Gustavo Eraldo da Silva
