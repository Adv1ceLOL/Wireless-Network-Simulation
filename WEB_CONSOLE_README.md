# 🌐 Wireless Sensor Network Simulator - Web Console

An interactive web-based console for the Wireless Sensor Network Simulator with comprehensive controls, real-time visualization, and step-by-step simulation capabilities.

## 🚀 Quick Start

### Method 1: Easy Startup (Recommended)
```bash
python start_web_console.py
```

### Method 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web console
python web_console.py
```

### Method 3: Install Web Dependencies Only
```bash
# Install just the web server dependencies
pip install flask==3.1.0 flask-socketio==5.4.1 python-socketio==5.11.4 eventlet==0.37.0

# Start the web console
python web_console.py
```

## 📱 Access the Interface

Once started, open your web browser and navigate to:
**http://localhost:5001**

## ✨ Features

### 🏗️ Network Management
- **Create Custom Networks**: Specify number of nodes, area size, and network parameters
- **Real-time Visualization**: Interactive D3.js-powered network visualization
- **Node Information**: Click nodes to see detailed information including position, connections, and message counts
- **Topology Controls**: Add or remove links between nodes with custom delays

### ⚡ Simulation Controls
- **Step-by-Step Execution**: Execute simulation one step at a time
- **Auto-Play Mode**: Automatic stepping with configurable delays
- **Parameter Control**: Adjust probabilities for packet requests, link failures, and new links
- **Real-time Statistics**: Monitor success rates, delays, and network changes

### 📨 Message Transmission
- **Path Visualization**: Visual highlighting of message transmission paths (automatic during simulation)
- **Transmission Statistics**: Success rates, delays, and failure tracking (automatic during simulation)

### 📊 Visualization Features
- **Visual Options**: Toggle node labels and transmission ranges
- **Path Highlighting**: Visualization of active transmission paths during simulation
- **Network Statistics**: Real-time display of network metrics

### 📈 Analytics & Monitoring
- **Live Statistics Panel**: 
  - Total requests and success rate
  - Average transmission delay
  - Links added/removed count
  - Message exchange counters
- **Node Details Panel**: Detailed information for selected nodes
- **Event Log**: Chronological log of all simulation events
- **Routing Tables**: View routing information for any node

## 🎮 Controls Guide

### Network Creation
1. Set the number of nodes (3-50)
2. Set the area size (5-20)
3. Click "Create Network"

### Running Simulations
1. **Single Step**: Click "Step Forward" to execute one simulation step
2. **Auto Play**: Click "Auto Play" for continuous stepping (use "Stop Auto" to pause)

### Topology Modification
1. Select two nodes (Node A and Node B)
2. Set link delay (for adding links)
3. Click "Add Link" or "Remove Link"

### Viewing Node Information
- **Click** any node to select it and see basic info
- **Double-click** any node to see detailed information
- **Click "Show Routing Info"** to see complete routing tables

## 🔧 Advanced Features

### Visualization Controls
- **Zoom**: Use mouse wheel or zoom buttons
- **Pan**: Click and drag empty space
- **Node Dragging**: Drag nodes to reposition them
- **Labels**: Toggle node ID labels on/off
- **Transmission Ranges**: Show/hide transmission range circles

### Auto-Play Configuration
The auto-play feature automatically executes simulation steps with a configurable delay. Events that can occur:
- Random packet transmission requests
- Random link failures
- Random new link formation
- Automatic hello message exchanges

### Routing Information
Access detailed routing information including:
- **Routing Tables**: Next hop and cost for each destination
- **Distance Vectors**: Current distance estimates
- **Connection Lists**: Direct neighbor connections
- **Message Counters**: Per-node message type counts

## 🔍 Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install -r requirements.txt
```

**2. Port already in use**
- Check if another instance is running
- Kill the process: `lsof -ti:5001 | xargs kill -9` (macOS/Linux)
- Or change the port in `web_console.py`

**3. Browser connection issues**
- Ensure firewall allows connections to port 5001
- Try accessing via `http://127.0.0.1:5001` instead of localhost
- Check browser console for JavaScript errors

**4. Visualization not loading**
- Ensure D3.js library is accessible (internet connection required)
- Check browser developer tools for loading errors
- Try refreshing the page

### Performance Tips

**For Large Networks (20+ nodes):**
- Disable auto-play for better performance
- Hide transmission ranges to reduce rendering load
- Use step-by-step mode instead of auto-play

**For Slow Computers:**
- Reduce network size (use fewer nodes)
- Increase auto-play delay
- Close unnecessary browser tabs

## 🌟 Key Advantages Over Command Line

1. **Visual Understanding**: See network topology and changes in real-time
2. **Interactive Control**: Click, drag, and explore the network
3. **History Navigation**: Go back and forth through simulation steps
4. **Real-time Monitoring**: Live statistics and event logging
5. **Easy Experimentation**: Quick parameter changes and immediate results

## 🔮 Advanced Usage

### Custom Network Scenarios
1. Create a network with specific parameters
2. Use topology controls to create desired network shapes
3. Test different routing scenarios with message transmission

### Protocol Analysis
1. Run step-by-step simulations
2. Monitor routing table changes
3. Analyze convergence behavior

### Performance Testing
1. Create networks of different sizes
2. Test with varying failure rates
3. Monitor success rates and delays

## 📞 Support

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the terminal where you started the server for Python errors
3. Ensure all dependencies are properly installed
4. Try restarting the web console

## 🙏 Credits

Built with:
- **Backend**: Flask + Socket.IO for real-time communication
- **Frontend**: D3.js for interactive network visualization
- **Design**: Modern responsive web interface
- **Simulation Core**: Original Wireless Sensor Network Simulator

Enjoy exploring wireless sensor networks with this powerful web-based tool! 🚀
