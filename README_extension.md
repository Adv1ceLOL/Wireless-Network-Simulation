## Testing

To test the functionality:

```bash
python test_simple.py
```

To run multiple iterations with different parameters:

```bash
python test_iterations.py [number_of_iterations]
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

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- Based on the wireless networks course at UFPB
- Special thanks to the original authors: Marismar da Costa Silva and Gustavo Eraldo da Silva
