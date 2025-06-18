from PIL import Image, ImageDraw

def visualize_network_pil(network, output_file="network_visualization_simple.png"):
    """Create a simple network visualization using PIL as a fallback when matplotlib is not available."""
    try:
        # Define canvas size and scaling factor
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Find min/max coordinates to scale appropriately
        min_x = min(node.x for node in network.nodes)
        max_x = max(node.x for node in network.nodes)
        min_y = min(node.y for node in network.nodes)
        max_y = max(node.y for node in network.nodes)
        
        # Add some padding
        padding = 0.1
        range_x = max_x - min_x
        range_y = max_y - min_y
        min_x -= range_x * padding
        max_x += range_x * padding
        min_y -= range_y * padding
        max_y += range_y * padding
        
        # Define scaling functions
        def scale_x(x):
            return int(((x - min_x) / (max_x - min_x)) * (width - 40) + 20)
        
        def scale_y(y):
            return int(((y - min_y) / (max_y - min_y)) * (height - 40) + 20)
        
        # Draw connections
        for node in network.nodes:
            x1, y1 = scale_x(node.x), scale_y(node.y)
            for neighbor_id, delay in node.connections.items():
                if node.node_id < neighbor_id:  # Draw each connection only once
                    neighbor = network.get_node_by_id(neighbor_id)
                    x2, y2 = scale_x(neighbor.x), scale_y(neighbor.y)
                    
                    # Calculate color based on delay (red = high delay, green = low delay)
                    r = int(255 * delay)
                    g = int(255 * (1 - delay))
                    b = 0
                    
                    # Draw the line
                    draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=1)
                    
                    # Draw delay text at midpoint
                    mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
                    draw.text((mid_x, mid_y), f"{delay:.2f}", fill=(0, 0, 0))
        
        # Draw nodes and transmission ranges
        for node in network.nodes:
            x, y = scale_x(node.x), scale_y(node.y)
            
            # Draw transmission range circle
            radius = int(node.transmission_range * (width - 40) / (max_x - min_x))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), 
                         outline=(200, 200, 255), fill=(240, 240, 255, 128))
            
            # Draw node
            node_radius = 10
            draw.ellipse((x - node_radius, y - node_radius, x + node_radius, y + node_radius), 
                         outline=(0, 0, 0), fill=(100, 149, 237))
            
            # Draw node ID
            draw.text((x - 3, y - 7), str(node.node_id), fill=(0, 0, 0))
        
        # Draw title and legend
        title = "Wireless Sensor Network (Simple Visualization)"
        draw.text((width // 2 - 150, 10), title, fill=(0, 0, 0))
        
        # Save the image
        img.save(output_file)
        print(f"Saved simple network visualization to {output_file}")
        
    except Exception as e:
        print(f"Error in PIL visualization: {e}")
        raise
