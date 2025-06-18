# Dynamic Scenario Simulation for Wireless Networks

This feature allows simulating dynamic scenarios in the wireless network where links can fail, new links can form, and packet transmission requests occur probabilistically over time.

## Overview

The dynamic scenario simulation allows testing the network's adaptability to changing conditions by:

1. Simulating probabilistic events at each time step:
   - Random packet transmission requests
   - Random link failures
   - Random new link formations

2. Tracking how the proactive distance vector protocol responds to these changes:
   - Convergence speed after topology changes
   - Success rate of packet transmissions
   - Average delay of successful transmissions

## Usage

Run a dynamic scenario simulation with:

```bash
python simulation.py --dynamic [options]
```

### Command-line Options

- `--dynamic`: Enables dynamic scenario simulation
- `--time-steps=<number>`: Number of time steps to simulate (default: 20)
- `--p-request=<float>`: Probability of a packet request at each time step (default: 0.3)
- `--p-fail=<float>`: Probability of a random link failure at each time step (default: 0.1)
- `--p-new=<float>`: Probability of a new link formation at each time step (default: 0.1)
- `--delay=<float>`: Delay between time steps in seconds (default: 1.0)
- `--interactive`: Show interactive visualizations at each time step
- `--nodes=<number>`: Number of nodes in the network (default: 15)

### Example Commands

```bash
# Basic dynamic scenario with default parameters
python simulation.py --dynamic

# More active scenario with higher probabilities
python simulation.py --dynamic --p-request=0.5 --p-fail=0.2 --p-new=0.3

# Interactive visualization of the dynamic scenario
python simulation.py --dynamic --interactive

# Short scenario with only 10 time steps
python simulation.py --dynamic --time-steps=10 --delay=0.5
```

## How It Works

At each time step, the simulation:

1. **Link Failure**: With probability `p_fail`, randomly removes an existing link
2. **New Link**: With probability `p_new`, adds a new link between two previously unconnected nodes (if they're within range)
3. **Packet Request**: With probability `p_request`, generates a packet transmission request between random source and destination

After each topology change (link failure or addition), the proactive distance vector protocol automatically runs to update routing tables across the network.

## Interactive Mode

In interactive mode (`--interactive`), the simulation displays:
- Network visualization after each time step
- Real-time updates showing routing table changes
- Visual representation of link failures and additions

The simulation pauses after each time step, allowing you to examine the network state before proceeding to the next step.

## Statistics

At the end of the simulation, detailed statistics are provided:
- Number of packet requests
- Success rate of transmissions
- Average delay for successful transmissions
- Number of links removed and added
- Total protocol reconvergence iterations
- Average iterations per topology change

## Use Cases

1. **Resilience Testing**: Test how well the network maintains connectivity when links fail
2. **Protocol Performance**: Measure how quickly the routing protocol adapts to changes
3. **Network Design**: Identify weak points in network topology
4. **Optimization**: Tune parameters to improve resilience and efficiency

## Notes

- Higher values for `p_fail` and `p_new` will result in more dynamic network behavior
- Smaller networks may become disconnected quickly with high failure rates
- In some network topologies, certain nodes may become isolated after link failures
