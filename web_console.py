#!/usr/bin/env python3
"""
Web Console for Wireless Sensor Network Simulation
Interactive web interface with full simulation controls and real-time visualization.
"""

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os
import sys
import threading
import time
import copy
import random
import argparse
from typing import Union, Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.network import SensorNetwork

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wireless_sensor_network_simulator_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@socketio.on_error_default
def default_error_handler(e):
    """Catch-all error handler for SocketIO events to prevent client disconnects."""
    logger.error(f"SocketIO handler error: {e}", exc_info=True)
    try:
        # Try to emit a user-friendly error message
        emit('app_error', {
            'message': 'Internal server error occurred. Please try again.',
            'details': str(e)
        })
    except Exception as emit_error:
        # If we can't emit, at least log it
        logger.error(f"Failed to emit error message after handler error: {emit_error}", exc_info=True)

class SimulationState:
    """Manages the complete state of the simulation with history for step navigation."""
    
    def __init__(self):
        self.network: Optional[SensorNetwork] = None
        self.history: List[Dict[str, Any]] = []
        self.current_step: int = 0
        self.max_steps: int = 0
        self.is_running: bool = False
        self.auto_play: bool = False
        self.auto_play_delay: float = 1.0
        self.simulation_params: Dict[str, Any] = {
            'n_nodes': 10,
            'area_size': 10,
            'p_request': 0.3,
            'p_fail': 0.1,
            'p_new': 0.1,
            'time_steps': 20
        }
        self.statistics: Dict[str, Any] = {
            'requests': 0,
            'successful_transmissions': 0,
            'failed_transmissions': 0,
            'links_removed': 0,
            'links_added': 0,
            'total_delay': 0,
            'reconvergence_iterations': 0,
            'total_messages': 0
        }
        self.selected_nodes: List[int] = []
        self.routing_visualization: Dict[str, Any] = {}
        
    def save_state(self, step_info: str = "", event_data: Optional[Dict[str, Any]] = None):
        """Save current network state to history."""
        if self.network is None:
            return

        # Ensure event_data is initialized as a dictionary if None
        event_data = event_data or {}

        state: Dict[str, Any] = {
            'step': self.current_step,
            'timestamp': datetime.now().isoformat(),
            'info': step_info,
            'network_snapshot': self._serialize_network(),
            'statistics': copy.deepcopy(self.statistics),
            'event_data': event_data,
            'routing_tables': self._get_routing_tables(),
            'message_counts': self._get_message_counts()
        }

        # If we're not at the end of history, truncate future states
        if self.current_step < len(self.history):
            self.history = self.history[:self.current_step]

        self.history.append(state)
        self.max_steps = len(self.history) - 1
        
    def _serialize_network(self) -> Dict[str, Any]:
        """Serialize network state for storage."""
        if not self.network:
            return {}
            
        nodes_data = []
        for node in self.network.nodes:
            node_data = {
                'id': node.node_id,
                'x': node.x,
                'y': node.y,
                'transmission_range': node.transmission_range,
                'connections': dict(node.connections),
                'routing_table': dict(node.routing_table),
                'distance_vector': dict(node.distance_vector)
            }
            nodes_data.append(node_data)
            
        links_data = []
        for link in self.network.get_all_links():
            links_data.append({
                'source': link[0],
                'target': link[1],
                'delay': link[2]
            })
            
        return {
            'nodes': nodes_data,
            'links': links_data
        }
        
    def _get_routing_tables(self) -> Dict[int, Dict[int, Tuple[Optional[int], float]]]:
        """Get routing tables for all nodes."""
        if not self.network:
            return {}

        routing_tables: Dict[int, Dict[int, Tuple[Optional[int], float]]] = {}
        for node in self.network.nodes:
            routing_tables[node.node_id] = {
                dest: (next_hop, cost)
                for dest, (next_hop, cost) in node.routing_table.items()
            }
        return routing_tables

    
    def _get_message_counts(self) -> Dict[int, Dict[str, int]]:
        """Get message counts for all nodes."""
        if not self.network:
            return {}

        message_counts: Dict[int, Dict[str, int]] = {}
        for node in self.network.nodes:
            message_counts[node.node_id] = {
                'hello_msg_count': getattr(node, 'hello_msg_count', 0),
                'topology_msg_count': getattr(node, 'topology_msg_count', 0),
                'route_discovery_msg_count': getattr(node, 'route_discovery_msg_count', 0),
                'data_packet_count': getattr(node, 'data_packet_count', 0)
            }
        return message_counts
        
    def goto_step(self, step: int) -> bool:
        """Navigate to a specific step in history."""
        if 0 <= step < len(self.history):
            self.current_step = step
            self._restore_state(self.history[step])
            return True
        return False
        
    def _restore_state(self, state: Dict[str, Any]):
        """Restore network state from history."""
        # This is a simplified restoration - in practice you'd need to 
        # reconstruct the full network object
        self.statistics = copy.deepcopy(state['statistics'])
        
    def step_forward(self) -> bool:
        """Move to next step."""
        if self.current_step < self.max_steps:
            self.current_step += 1
            self._restore_state(self.history[self.current_step])
            return True
        return False
        
    def step_backward(self) -> bool:
        """Move to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._restore_state(self.history[self.current_step])
            return True
        return False

# Global simulation state
simulation = SimulationState()

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/test_socketio')
def test_socketio():
    """Serve the Socket.IO test page."""
    with open('test_socketio.html', 'r') as f:
        return f.read()

@app.route('/test_create')
def test_create():
    """Test route to manually trigger network creation."""
    logger.info("Test route called - manually triggering network creation")
    
    # Simulate the socket event
    data = {
        'params': {
            'n_nodes': 10,
            'area_size': 10,
            'p_request': 0.3,
            'p_fail': 0.1,
            'p_new': 0.1
        }
    }
    
    try:
        handle_create_network(data)
        return {"status": "success", "message": "Network creation triggered"}
    except Exception as e:
        logger.error(f"Test create failed: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/static/<path:filename>')
def serve_static(filename: str) -> Any:
    """Serve static files."""
    return send_from_directory('static', filename)

@app.route('/test_socket.html')
def test_socket():
    """Serve the test Socket.IO page."""
    with open('test_socket.html', 'r') as f:
        return f.read()

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    emit('simulation_state', get_simulation_status())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

@socketio.on('create_network')
def handle_create_network(data: Dict[str, Any]) -> None:
    """Create a new network with specified parameters."""
    logger.info(f"Received create_network request with data: {data}")
    try:
        params: Dict[str, Any] = data.get('params', {})
        logger.info(f"Network parameters: {params}")
        simulation.simulation_params.update(params)
        
        # Create new network
        logger.info("Creating new SensorNetwork...")
        simulation.network = SensorNetwork()
        seed = simulation.simulation_params.get('seed') if 'seed' in simulation.simulation_params else None
        simulation.network.create_random_network(
            n=simulation.simulation_params['n_nodes'],
            area_size=simulation.simulation_params['area_size'],
            seed=seed
        )
        logger.info(f"Network created with {len(simulation.network.nodes)} nodes")
        
        # Initialize routing
        logger.info("Running distance vector protocol...")
        iterations = simulation.network.run_distance_vector_protocol(verbose=False)
        logger.info(f"Protocol converged after {iterations} iterations")
        
        # Reset state
        simulation.history = []
        simulation.current_step = 0
        simulation.statistics = {
            'requests': 0,
            'successful_transmissions': 0,
            'failed_transmissions': 0,
            'links_removed': 0,
            'links_added': 0,
            'total_delay': 0,
            'reconvergence_iterations': iterations,
            'total_messages': 0
        }
        
        # Save initial state
        simulation.save_state(f"Network created with {simulation.simulation_params['n_nodes']} nodes")
        
        network_data = get_network_data()
        logger.info(f"Network data prepared: {len(network_data['nodes'])} nodes, {len(network_data['links'])} links")
        
        response_data = {
            'success': True,
            'message': f'Network created with {len(simulation.network.nodes)} nodes',
            'network_data': network_data,
            'statistics': simulation.statistics
        }
        
        emit('network_created', response_data)
        emit('simulation_state', get_simulation_status())
        logger.info("Network creation completed successfully")
        
    except Exception as e:
        logger.error(f"Error creating network: {str(e)}", exc_info=True)
        emit('app_error', {'message': f'Error creating network: {str(e)}'})

@socketio.on('update_parameters')
def handle_update_parameters(data: Dict[str, Any]) -> None:
    """Update simulation parameters without recreating the network."""
    try:
        params: Dict[str, Any] = data.get('params', {})
        logger.info(f"Updating simulation parameters: {params}")
        
        # Update only the probability parameters, not network structure parameters
        if 'p_request' in params:
            simulation.simulation_params['p_request'] = params['p_request']
        if 'p_fail' in params:
            simulation.simulation_params['p_fail'] = params['p_fail']
        if 'p_new' in params:
            simulation.simulation_params['p_new'] = params['p_new']
        if 'time_steps' in params:
            simulation.simulation_params['time_steps'] = params['time_steps']
            
        logger.info(f"Updated simulation parameters: {simulation.simulation_params}")
        
        emit('parameters_updated', {
            'success': True,
            'message': 'Simulation parameters updated',
            'parameters': simulation.simulation_params
        })
        
    except Exception as e:
        logger.error(f"Error updating parameters: {str(e)}", exc_info=True)
        emit('app_error', {'message': f'Error updating parameters: {str(e)}'})

@socketio.on('step_simulation')
def handle_step_simulation(data: Optional[Dict[str, Any]] = None):
    """Execute one simulation step with current parameters."""
    try:
        if not simulation.network:
            emit('app_error', {'message': 'No network created'})
            return
            
        # If parameters are provided with the step request, update them first
        if data and 'params' in data:
            params = data['params']
            logger.info(f"Updating parameters for step: {params}")
            if 'p_request' in params:
                simulation.simulation_params['p_request'] = params['p_request']
            if 'p_fail' in params:
                simulation.simulation_params['p_fail'] = params['p_fail']
            if 'p_new' in params:
                simulation.simulation_params['p_new'] = params['p_new']
            
        # Execute one step of the dynamic simulation
        result = execute_simulation_step()
        
        if result:
            simulation.save_state(f"Step {simulation.current_step + 1}", result)
            simulation.current_step = len(simulation.history) - 1
            
            emit('step_completed', {
                'step': simulation.current_step,
                'result': result,
                'network_data': get_network_data(),
                'statistics': simulation.statistics
            })
            
            emit('simulation_state', get_simulation_status())
        
    except Exception as e:
        logger.error(f"Error in step simulation: {str(e)}")
        emit('app_error', {'message': f'Error in step simulation: {str(e)}'})

@socketio.on('navigate_step')
def handle_navigate_step(data: Dict[str, Union[str, int]]) -> None:
    """Navigate to a specific step."""
    try:
        direction: Optional[str] = str(data.get('direction')) if 'direction' in data else None
        step: Optional[int] = int(data['step']) if 'step' in data else None
        
        success = False
        if direction == 'forward':
            success = simulation.step_forward()
        elif direction == 'backward':
            success = simulation.step_backward()
        elif direction == 'goto' and step is not None:
            success = simulation.goto_step(step)
        elif direction == 'first':
            success = simulation.goto_step(0)
        elif direction == 'last':
            success = simulation.goto_step(simulation.max_steps)
            
        if success:
            emit('navigation_complete', {
                'current_step': simulation.current_step,
                'network_data': get_network_data(),
                'statistics': simulation.statistics
            })
            emit('simulation_state', get_simulation_status())
        else:
            emit('app_error', {'message': 'Navigation failed'})
            
    except Exception as e:
        logger.error(f"Error in navigation: {str(e)}")
        emit('app_error', {'message': f'Error in navigation: {str(e)}'})

@socketio.on('modify_topology')
def handle_modify_topology(data):
    """Modify network topology by adding/removing links."""
    try:
        action = data.get('action')  # 'add_link', 'remove_link'
        node_a = data.get('node_a')
        node_b = data.get('node_b')
        delay = data.get('delay', 1.0)
        
        if not simulation.network:
            emit('app_error', {'message': 'No network created'})
            return
            
        if action == 'add_link':
            # Validate that nodes are within transmission range
            node_a_obj = simulation.network.get_node_by_id(node_a)
            node_b_obj = simulation.network.get_node_by_id(node_b)
            
            if not node_a_obj or not node_b_obj:
                emit('app_error', {'message': f'Node {node_a} or {node_b} not found'})
                return
                  # Check if at least one node can reach the other
            distance = node_a_obj.distance_to(node_b_obj)
            
            # Only allow link creation if both nodes can reach each other
            if distance <= node_a_obj.transmission_range and distance <= node_b_obj.transmission_range:
                # Both nodes can reach each other, allow link creation
                pass
            else:
                emit('app_error', {
                    'message': f'Cannot create link: Nodes {node_a} and {node_b} are not mutually reachable\n'
                              f'Distance: {distance:.2f}, Both nodes need range ≥ {distance:.2f}, Available ranges: {node_a_obj.transmission_range:.2f}, {node_b_obj.transmission_range:.2f}'
                })
                return
            
            iterations = simulation.network.handle_topology_change(
                node_a, node_b, new_delay=delay, verbose=False
            )
            simulation.statistics['links_added'] += 1
            simulation.statistics['reconvergence_iterations'] += iterations
            message = f"Link added: {node_a} <-> {node_b}"
            
        elif action == 'remove_link':
            # Allow removal of any link, even if it isolates nodes
            iterations = simulation.network.handle_topology_change(
                node_a, node_b, new_delay=None, verbose=False, 
                auto_reconnect=False  # Never reconnect
            )
            
            simulation.statistics['links_removed'] += 1
            simulation.statistics['reconvergence_iterations'] += iterations
            message = f"Link removed: {node_a} <-> {node_b}"
              # Check if any nodes were isolated and report but don't prevent
            reconnection_info = getattr(simulation.network, '_last_reconnection_info', None)
            if reconnection_info and reconnection_info.get('isolated_nodes'):
                isolated_nodes = reconnection_info.get('isolated_nodes', [])
                if isolated_nodes:
                    message += f"\nWarning: Node(s) {', '.join(map(str, isolated_nodes))} became isolated"
                    # Add a note suggesting reconnection for isolated nodes
                    message += "\nSuggestion: Consider adding new links to reconnect isolated nodes"
        else:
            emit('app_error', {'message': 'Invalid topology action'})
            return
            
        topology_change = {
            'action': action,
            'node_a': node_a,
            'node_b': node_b,
            'delay': delay if action == 'add_link' else None,
            'iterations': iterations,
            'reconnection_info': getattr(simulation.network, '_last_reconnection_info', None)
        }
        
        simulation.save_state(message, {'topology_change': topology_change})
        
        emit('topology_modified', {
            'change': topology_change,
            'message': message,
            'statistics': simulation.statistics,
            'network_data': get_network_data()
        })
        
    except Exception as e:
        logger.error(f"Error modifying topology: {str(e)}")
        emit('app_error', {'message': f'Error modifying topology: {str(e)}'})

@socketio.on('get_routing_info')
def handle_get_routing_info(data):
    """Get detailed routing information for selected nodes."""
    try:
        node_ids = data.get('node_ids', [])
        
        if not simulation.network:
            emit('app_error', {'message': 'No network created'})
            return
            
        routing_info = {}
        for node_id in node_ids:
            node = simulation.network.get_node_by_id(node_id)
            if node:
                routing_info[node_id] = {
                    'routing_table': dict(node.routing_table),
                    'distance_vector': dict(node.distance_vector),
                    'connections': dict(node.connections),
                    'message_counts': {
                        'hello_msg_count': getattr(node, 'hello_msg_count', 0),
                        'topology_msg_count': getattr(node, 'topology_msg_count', 0),
                        'route_discovery_msg_count': getattr(node, 'route_discovery_msg_count', 0),
                        'data_packet_count': getattr(node, 'data_packet_count', 0)
                    }
                }
                
        emit('routing_info', routing_info)
        
    except Exception as e:
        logger.error(f"Error getting routing info: {str(e)}")
        emit('app_error', {'message': f'Error getting routing info: {str(e)}'})

@socketio.on('start_auto_play')
def handle_start_auto_play(data):
    """Start automatic step execution."""
    try:
        simulation.auto_play = True
        simulation.auto_play_delay = data.get('delay', 1.0)
        
        # Update parameters if provided
        if 'params' in data:
            params = data['params']
            if 'p_request' in params:
                simulation.simulation_params['p_request'] = params['p_request']
            if 'p_fail' in params:
                simulation.simulation_params['p_fail'] = params['p_fail']
            if 'p_new' in params:
                simulation.simulation_params['p_new'] = params['p_new']
            logger.info(f"Updated parameters for auto-play: {simulation.simulation_params}")
        
        def auto_play_thread():
            while simulation.auto_play and simulation.network:
                time.sleep(simulation.auto_play_delay)
                if simulation.auto_play:  # Check again in case it was stopped
                    socketio.emit('auto_step_trigger')
                    
        threading.Thread(target=auto_play_thread, daemon=True).start()
        emit('auto_play_started', {'delay': simulation.auto_play_delay})
        
    except Exception as e:
        logger.error(f"Error starting auto play: {str(e)}")
        emit('app_error', {'message': f'Error starting auto play: {str(e)}'})

@socketio.on('stop_auto_play')
def handle_stop_auto_play():
    """Stop automatic step execution."""
    simulation.auto_play = False
    emit('auto_play_stopped')

@socketio.on('export_data')
def handle_export_data(data):
    """Export simulation data in various formats."""
    try:
        export_type = data.get('type', 'json')  # json, csv, report
        
        if export_type == 'json':
            export_data = {
                'network': simulation._serialize_network(),
                'history': simulation.history,
                'statistics': simulation.statistics,
                'parameters': simulation.simulation_params
            }
            emit('data_exported', {
                'type': 'json',
                'data': export_data,
                'filename': f'simulation_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            })
            
        elif export_type == 'report' and simulation.network:
            # Generate a detailed report
            report_content = generate_detailed_report()
            emit('data_exported', {
                'type': 'report',
                'data': report_content,
                'filename': f'simulation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            })
            
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        emit('app_error', {'message': f'Error exporting data: {str(e)}'})

def execute_simulation_step() -> Dict[str, Any]:
    """Execute one step of the dynamic simulation."""
    
    if not simulation.network:
        return {}
        
    step_events = []
    
    # 1. Hello message exchange
    for node in simulation.network.nodes:
        hello_msgs = len(node.connections)
        node.hello_msg_count += hello_msgs
        
    # 2. Random link failure
    if random.random() < simulation.simulation_params['p_fail']:
        links = simulation.network.get_all_links()
        
        if links:  # Only try to remove if there are links
            node_a_id, node_b_id, _ = random.choice(links)
            iterations = simulation.network.handle_topology_change(
                node_a_id, node_b_id, new_delay=None, verbose=False,
                auto_reconnect=False  # Never reconnect
            )
            simulation.statistics['links_removed'] += 1
            simulation.statistics['reconvergence_iterations'] += iterations
            step_events.append(f"Link removed: {node_a_id}-{node_b_id}")
            
    # 3. Random new link with balanced probability
    # Scale the probability based on the ratio of possible new links to existing links
    links = simulation.network.get_all_links()
    n_nodes = len(simulation.network.nodes)
    max_possible_links = (n_nodes * (n_nodes - 1)) // 2  # Maximum possible undirected links
    current_links = len(links)
      # The more connected the network is, the lower the probability of adding new links
    # to balance with link removal over time
    effective_p_new = simulation.simulation_params['p_new'] * ((max_possible_links - current_links) / max_possible_links)
    
    # Find isolated nodes (nodes with no connections)
    isolated_nodes = [i for i, node in enumerate(simulation.network.nodes) if len(node.connections) == 0]
    
    # Increase the probability if there are isolated nodes to prioritize reconnection
    if isolated_nodes:
        effective_p_new = max(effective_p_new, 0.5)  # Ensure higher probability for reconnection
    
    if random.random() < effective_p_new or isolated_nodes:  # Always try to add links if there are isolated nodes
        prioritized_pairs = []
        regular_pairs = []
        
        # First check for pairs involving isolated nodes
        for isolated_node_id in isolated_nodes:
            node_i = simulation.network.nodes[isolated_node_id]
            for j in range(n_nodes):
                if isolated_node_id != j:
                    node_j = simulation.network.nodes[j]
                    # Only add pairs that are mutually within transmission range
                    if node_i.can_reach(node_j) and node_j.can_reach(node_i):
                        prioritized_pairs.append((isolated_node_id, j))
        
        # Only check regular pairs if no prioritized pairs found
        if not prioritized_pairs:
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    if j not in simulation.network.nodes[i].connections:
                        node_i = simulation.network.nodes[i]
                        node_j = simulation.network.nodes[j]
                        # Only add pairs that are mutually within transmission range
                        if node_i.can_reach(node_j) and node_j.can_reach(node_i):
                            regular_pairs.append((i, j))
          # Choose pairs from prioritized list if available, otherwise from regular list
        unconnected_pairs = prioritized_pairs if prioritized_pairs else regular_pairs
        
        if unconnected_pairs:
            node_a_id, node_b_id = random.choice(unconnected_pairs)
            delay = random.uniform(0.1, 1.0)
            iterations = simulation.network.handle_topology_change(
                node_a_id, node_b_id, new_delay=delay, verbose=False
            )
            simulation.statistics['links_added'] += 1
            simulation.statistics['reconvergence_iterations'] += iterations
            
            # Indicate if this was a priority reconnection for an isolated node
            was_isolated = node_a_id in isolated_nodes or node_b_id in isolated_nodes
            priority_msg = " (priority reconnection)" if was_isolated else f" (p={effective_p_new:.3f})"
            step_events.append(f"Link added: {node_a_id}-{node_b_id}{priority_msg}")
            
    # 4. Random packet request
    if random.random() < simulation.simulation_params['p_request']:
        n_nodes = len(simulation.network.nodes)
        source_id = random.randint(0, n_nodes - 1)
        dest_id = random.randint(0, n_nodes - 1)
        while dest_id == source_id:
            dest_id = random.randint(0, n_nodes - 1)
            
        try:
            # Perform transmission (always attempt, let the function handle routing logic)
            result = simulation.network.simulate_message_transmission(
                source_id, dest_id, "Auto packet", verbose=False
            )
            
            # Result is always a 3-tuple: (path, delay, error_reason)
            if result and len(result) == 3:
                path, delay, error_reason = result
                simulation.statistics['requests'] += 1
                
                if path and len(path) > 0 and delay != float('inf') and error_reason is None:
                    simulation.statistics['successful_transmissions'] += 1
                    simulation.statistics['total_delay'] += delay
                    step_events.append(f"Transmission: {source_id}->{dest_id} succeeded (path: {' -> '.join(map(str, path))})")
                    
                    # Update data packet counts
                    for node_id in path:
                        node = simulation.network.get_node_by_id(node_id)
                        if node and hasattr(node, 'data_packet_count'):
                            node.data_packet_count += 1
                else:
                    simulation.statistics['failed_transmissions'] += 1
                    reason = error_reason if error_reason else "no path available"
                    step_events.append(f"Transmission: {source_id}->{dest_id} failed ({reason})")
            else:
                simulation.statistics['requests'] += 1
                simulation.statistics['failed_transmissions'] += 1
                step_events.append(f"Transmission: {source_id}->{dest_id} failed (invalid result format)")
                
        except Exception as e:
            # Handle transmission errors gracefully
            logger.warning(f"Auto transmission error: {str(e)}")
            simulation.statistics['requests'] += 1
            simulation.statistics['failed_transmissions'] += 1
            step_events.append(f"Transmission: {source_id}->{dest_id} failed (error: {str(e)[:50]})")
            
    return {
        'step': simulation.current_step + 1,
        'events': step_events,
        'timestamp': datetime.now().isoformat()
    }

def get_network_data() -> Dict[str, Any]:
    """Get current network data for visualization."""
    if not simulation.network:
        return {'nodes': [], 'links': []}
        
    nodes = []
    for node in simulation.network.nodes:
        is_isolated = len(node.connections) == 0
        nodes.append({
            'id': node.node_id,
            'x': node.x,
            'y': node.y,
            'transmission_range': node.transmission_range,
            'connections': len(node.connections),
            'neighbors': list(node.connections.keys()),
            'neighbor_delays': node.connections,
            'is_isolated': is_isolated,
            'message_counts': {
                'hello': getattr(node, 'hello_msg_count', 0),
                'topology': getattr(node, 'topology_msg_count', 0),
                'route_discovery': getattr(node, 'route_discovery_msg_count', 0),
                'data_packets': getattr(node, 'data_packet_count', 0)
            }
        })
        
    links = []
    for link in simulation.network.get_all_links():
        links.append({
            'source': link[0],
            'target': link[1],
            'delay': link[2]
        })
        
    return {'nodes': nodes, 'links': links}

def get_simulation_status() -> Dict[str, Any]:
    """Get current simulation status."""
    return {
        'has_network': simulation.network is not None,
        'current_step': simulation.current_step,
        'max_steps': simulation.max_steps,
        'auto_play': simulation.auto_play,
        'parameters': simulation.simulation_params,
        'statistics': simulation.statistics
    }

def generate_detailed_report() -> str:
    """Generate a detailed text report of the simulation."""
    if not simulation.network:
        return "No network data available"
        
    report = []
    report.append("=" * 70)
    report.append("WIRELESS SENSOR NETWORK SIMULATION REPORT")
    report.append("=" * 70)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Network parameters
    report.append("NETWORK PARAMETERS:")
    for key, value in simulation.simulation_params.items():
        report.append(f"  {key}: {value}")
    report.append("")
    
    # Statistics
    report.append("SIMULATION STATISTICS:")
    for key, value in simulation.statistics.items():
        report.append(f"  {key}: {value}")
    report.append("")
    
    # Network topology
    report.append("NETWORK TOPOLOGY:")
    report.append(f"Nodes: {len(simulation.network.nodes)}")
    report.append(f"Links: {len(simulation.network.get_all_links())}")
    report.append("")
    
    # Node details
    report.append("NODE DETAILS:")
    for node in simulation.network.nodes:
        report.append(f"  Node {node.node_id}:")
        report.append(f"    Position: ({node.x:.2f}, {node.y:.2f})")
        report.append(f"    Transmission Range: {node.transmission_range:.2f}")
        report.append(f"    Connections: {len(node.connections)}")
        report.append(f"    Messages - Hello: {getattr(node, 'hello_msg_count', 0)}, "
                     f"Topology: {getattr(node, 'topology_msg_count', 0)}, "
                     f"Route Discovery: {getattr(node, 'route_discovery_msg_count', 0)}, "
                     f"Data Packets: {getattr(node, 'data_packet_count', 0)}")
        report.append("")
        
    return "\n".join(report)

def check_network_connectivity() -> Dict[str, Any]:
    """Check if the network is fully connected and identify partitions."""
    if not simulation.network:
        return {'connected': False, 'reason': 'No network exists'}
    
    nodes = simulation.network.nodes
    if not nodes:
        return {'connected': False, 'reason': 'No nodes in network'}
    
    # Check if all nodes can reach all other nodes
    unreachable_pairs = []
    total_pairs = 0
    
    for source in nodes:
        for target in nodes:
            if source.node_id != target.node_id:
                total_pairs += 1
                if target.node_id not in source.routing_table:
                    unreachable_pairs.append((source.node_id, target.node_id))
    
    connectivity_ratio = (total_pairs - len(unreachable_pairs)) / total_pairs if total_pairs > 0 else 0
    
    return {
        'connected': len(unreachable_pairs) == 0,
        'connectivity_ratio': connectivity_ratio,
        'unreachable_pairs': unreachable_pairs[:10],  # Limit to first 10 for display
        'total_unreachable': len(unreachable_pairs),
        'total_pairs': total_pairs
    }

@socketio.on('check_connectivity')
def handle_check_connectivity():
    """Check network connectivity and return status."""
    try:
        connectivity_status = check_network_connectivity()
        emit('connectivity_status', connectivity_status)
    except Exception as e:
        logger.error(f"Error checking connectivity: {str(e)}")
        emit('app_error', {'message': f'Error checking connectivity: {str(e)}'})

if __name__ == '__main__':
    """Run the web console application."""
    parser = argparse.ArgumentParser(description='Wireless Sensor Network Simulator Web Console')
    parser.add_argument('--host', default='127.0.0.1', help='Host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║               Wireless Sensor Network Simulator - Web Console            ║
╚══════════════════════════════════════════════════════════════════════════╝

Starting web console...
🌐 Server: http://{args.host}:{args.port}
📊 Real-time visualization and control interface
🎮 Interactive simulation controls
📈 Live statistics and reporting

Press Ctrl+C to stop the server
""")
    
    try:
        socketio.run(app, host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down web console...")
    except Exception as e:
        print(f"Error starting server: {e}")
