// Wireless Sensor Network Simulator - Web Console JavaScript
class NetworkSimulator {
    constructor() {
        this.socket = null;
        this.networkData = { nodes: [], links: [] };
        this.svg = null;
        this.simulation = null;
        this.transform = d3.zoomIdentity;
        this.selectedNodes = [];
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.initSocket();
        this.initUI();
        this.initVisualization();
        this.bindEvents();
    }
    
    initSocket() {
        console.log('Initializing Socket.IO connection...');
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Socket.IO connected successfully');
            this.isConnected = true;
            this.updateConnectionStatus('Connected', true);
            this.log('Connected to server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Socket.IO disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', false);
            this.log('Disconnected from server', 'error');
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Socket.IO connection error:', error);
            this.log('Connection error: ' + error.message, 'error');
        });
        
        // Catch internal Socket.IO errors
        this.socket.on('error', (error) => {
            console.error('Socket.IO client error:', error);
        });
        
        this.socket.on('simulation_state', (data) => {
            this.updateSimulationState(data);
        });
        
        this.socket.on('network_created', (data) => {
            if (data.success) {
                // Clear existing node positions for new network
                this.nodePositions.clear();
                
                this.networkData = data.network_data;
                this.updateVisualization();
                this.updateNodeSelects();
                this.updateStatistics(data.statistics);
                this.log(data.message, 'success');
            } else {
                this.log('Failed to create network', 'error');
            }
        });
        
        this.socket.on('step_completed', (data) => {
            this.networkData = data.network_data;
            this.updateVisualization();
            this.updateStatistics(data.statistics);
            
            if (data.result && data.result.events) {
                data.result.events.forEach(event => {
                    this.log(`Step ${data.step}: ${event}`, 'info');
                });
            }
        });
        
        this.socket.on('navigation_complete', (data) => {
            this.networkData = data.network_data;
            this.updateVisualization();
            this.updateStatistics(data.statistics);
            this.log(`Navigated to step ${data.current_step}`, 'info');
        });
        

        
        this.socket.on('topology_modified', (data) => {
            this.updateStatistics(data.statistics);
            this.networkData = data.network_data;
            this.updateVisualization();
            this.updateNodeSelects();
            this.log(data.message, 'info');
            
            // Check for reconnection alerts
            if (data.change && data.change.reconnection_info && data.change.reconnection_info.reconnections) {
                const reconnections = data.change.reconnection_info.reconnections;
                for (const reconnection of reconnections) {
                    this.showAlert(
                        `Auto-Reconnection Alert`, 
                        `Node ${reconnection.isolated_node} was isolated after link removal and has been automatically reconnected to Node ${reconnection.connected_to} to maintain network connectivity.`,
                        'warning'
                    );
                }
            }
        });
        
        this.socket.on('routing_info', (data) => {
            this.showRoutingInfo(data);
        });
        
        this.socket.on('auto_play_started', (data) => {
            document.getElementById('autoPlay').disabled = true;
            document.getElementById('stopAutoPlay').disabled = false;
            this.log(`Auto-play started with ${data.delay}s delay`, 'info');
        });
        
        this.socket.on('auto_play_stopped', () => {
            document.getElementById('autoPlay').disabled = false;
            document.getElementById('stopAutoPlay').disabled = true;
            this.log('Auto-play stopped', 'info');
        });
        
        this.socket.on('auto_step_trigger', () => {
            this.stepSimulation();
        });
        
        this.socket.on('data_exported', (data) => {
            this.showExportModal(data);
        });
        
        this.socket.on('app_error', (data) => {
            // Application-level errors (e.g., invalid actions)
            this.log(data.message, 'error');
            this.showAlert('Error', data.message, 'error');
        });
    }
    
    initUI() {
        // Initialize UI state
        this.updateConnectionStatus('Connecting...', false);
    }
    
    initVisualization() {
        const container = d3.select('#networkVisualization');
        this.svg = container
            .attr('viewBox', '0 0 800 600')
            .style('background', '#fafbfc');
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 5])
            .on('zoom', (event) => {
                this.transform = event.transform;
                this.svg.select('.network-group').attr('transform', this.transform);
            });
        
        this.svg.call(zoom);
        
        // Create main group for network elements
        const networkGroup = this.svg.append('g').attr('class', 'network-group');
        
        // Create groups for different elements (order matters for layering)
        networkGroup.append('g').attr('class', 'transmission-ranges');
        networkGroup.append('g').attr('class', 'links');
        networkGroup.append('g').attr('class', 'nodes');
        networkGroup.append('g').attr('class', 'labels');
        
        // Store node positions to maintain consistency
        this.nodePositions = new Map();
        
        // Simple scale factor to map server coordinates to SVG coordinates
        this.scaleX = 60; // Scale factor for X coordinates
        this.scaleY = 60; // Scale factor for Y coordinates
        this.offsetX = 100; // Offset to center the network
        this.offsetY = 100; // Offset to center the network
    }
    
    bindEvents() {
        // Network creation
        document.getElementById('createNetwork').addEventListener('click', () => {
            this.createNetwork();
        });
        
        // Simulation controls
        document.getElementById('stepSimulation').addEventListener('click', () => {
            this.stepSimulation();
        });
        
        document.getElementById('autoPlay').addEventListener('click', () => {
            this.startAutoPlay();
        });
        
        document.getElementById('stopAutoPlay').addEventListener('click', () => {
            this.stopAutoPlay();
        });
        
        // Navigation controls
        document.getElementById('firstStep').addEventListener('click', () => {
            this.navigate('first');
        });
        
        document.getElementById('prevStep').addEventListener('click', () => {
            this.navigate('backward');
        });
        
        document.getElementById('nextStep').addEventListener('click', () => {
            this.navigate('forward');
        });
        
        document.getElementById('lastStep').addEventListener('click', () => {
            this.navigate('last');
        });
        
        document.getElementById('gotoStepBtn').addEventListener('click', () => {
            const step = parseInt(document.getElementById('gotoStep').value);
            this.navigate('goto', step);
        });
        
        // Topology controls
        document.getElementById('addLink').addEventListener('click', () => {
            this.modifyTopology('add_link');
        });
        
        document.getElementById('removeLink').addEventListener('click', () => {
            this.modifyTopology('remove_link');
        });
        
        // Visualization controls
        document.getElementById('zoomIn').addEventListener('click', () => {
            this.zoom(1.5);
        });
        
        document.getElementById('zoomOut').addEventListener('click', () => {
            this.zoom(0.75);
        });
        
        document.getElementById('resetZoom').addEventListener('click', () => {
            this.resetZoom();
        });
        
        document.getElementById('showLabels').addEventListener('change', (e) => {
            this.toggleLabels(e.target.checked);
        });
        
        document.getElementById('showRanges').addEventListener('change', (e) => {
            this.toggleTransmissionRanges(e.target.checked);
        });
        
        // Export controls
        document.getElementById('exportJSON').addEventListener('click', () => {
            this.exportData('json');
        });
        
        document.getElementById('exportReport').addEventListener('click', () => {
            this.exportData('report');
        });
        
        document.getElementById('exportImage').addEventListener('click', () => {
            this.exportImage();
        });
        
        // Clear log
        document.getElementById('clearLog').addEventListener('click', () => {
            this.clearLog();
        });

        // Modal events
        document.querySelectorAll('.close').forEach(close => {
            close.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });
        
        document.getElementById('closeExportModal').addEventListener('click', () => {
            document.getElementById('exportModal').style.display = 'none';
        });
        
        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }
    
    createNetwork() {
        console.log('Create network button clicked');
        const params = {
            n_nodes: parseInt(document.getElementById('nodeCount').value),
            area_size: parseInt(document.getElementById('areaSize').value),
            p_request: parseFloat(document.getElementById('pRequest').value),
            p_fail: parseFloat(document.getElementById('pFail').value),
            p_new: parseFloat(document.getElementById('pNew').value)
        };
        
        console.log('Network parameters:', params);
        console.log('Socket connected:', this.isConnected);
        console.log('Socket object:', this.socket);
        
        if (!this.socket) {
            console.error('Socket.IO not initialized');
            this.log('Socket.IO not initialized', 'error');
            return;
        }
        
        this.socket.emit('create_network', { params });
        console.log('Emitted create_network event');
    }
    
    stepSimulation() {
        this.socket.emit('step_simulation');
    }
    
    navigate(direction, step = null) {
        this.socket.emit('navigate_step', { direction, step });
    }
    

    
    modifyTopology(action) {
        const nodeA = parseInt(document.getElementById('nodeA').value);
        const nodeB = parseInt(document.getElementById('nodeB').value);
        const delay = parseFloat(document.getElementById('linkDelay').value);
        
        if (isNaN(nodeA) || isNaN(nodeB) || nodeA === nodeB) {
            this.log('Please select different nodes', 'error');
            return;
        }
        
        this.socket.emit('modify_topology', { action, node_a: nodeA, node_b: nodeB, delay });
    }
    
    startAutoPlay() {
        const delay = 1.0; // Could be made configurable
        this.socket.emit('start_auto_play', { delay });
    }
    
    stopAutoPlay() {
        this.socket.emit('stop_auto_play');
    }
    
    exportData(type) {
        this.socket.emit('export_data', { type });
    }
    
    exportImage() {
        // Get SVG element and convert to image
        const svg = document.getElementById('networkVisualization');
        const svgData = new XMLSerializer().serializeToString(svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        canvas.width = 800;
        canvas.height = 600;
        
        img.onload = () => {
            ctx.drawImage(img, 0, 0);
            const link = document.createElement('a');
            link.download = `network_visualization_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
            link.href = canvas.toDataURL();
            link.click();
        };
        
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);
        img.src = url;
    }
    
    updateVisualization() {
        if (!this.networkData || !this.networkData.nodes.length) return;
        
        // Prepare data with fixed positions
        const nodes = this.networkData.nodes.map(d => {
            // Use server-provided coordinates and scale them to SVG space
            const svgX = this.offsetX + (d.x * this.scaleX);
            const svgY = this.offsetY + (d.y * this.scaleY);
            
            // Store position for consistency
            if (!this.nodePositions.has(d.id)) {
                this.nodePositions.set(d.id, { x: svgX, y: svgY });
            }
            
            const position = this.nodePositions.get(d.id);
            return { 
                ...d, 
                x: position.x, 
                y: position.y,
                fx: position.x, // Fix position
                fy: position.y  // Fix position
            };
        });
        
        const links = this.networkData.links.map(d => ({
            source: d.source,
            target: d.target,
            delay: d.delay
        }));
        
        // Update links
        const link = this.svg.select('.links')
            .selectAll('.link')
            .data(links, d => `${d.source}-${d.target}`);
        
        link.exit().remove();
        
        const linkEnter = link.enter()
            .append('line')
            .attr('class', 'link')
            .style('stroke', '#999')
            .style('stroke-width', 2)
            .style('opacity', 0.7);
        
        linkEnter.append('title')
            .text(d => `Delay: ${d.delay.toFixed(3)}`);
        
        // Update nodes
        const node = this.svg.select('.nodes')
            .selectAll('.node')
            .data(nodes, d => d.id);
        
        node.exit().remove();
        
        const nodeEnter = node.enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', 15)
            .style('fill', '#3498db')
            .style('cursor', 'pointer')
            .on('click', (event, d) => {
                this.selectNode(d);
            })
            .on('dblclick', (event, d) => {
                this.showNodeInfo(d);
            });
        
        nodeEnter.append('title')
            .text(d => `Node ${d.id}\nPosition: (${d.x?.toFixed(2) || 0}, ${d.y?.toFixed(2) || 0})\nConnections: ${d.connections}`);
        
        // Update labels
        const labels = this.svg.select('.labels')
            .selectAll('.node-label')
            .data(nodes, d => d.id);
        
        labels.exit().remove();
        
        labels.enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', 4)
            .style('font-size', '12px')
            .style('font-weight', 'bold')
            .style('fill', '#2c3e50')
            .style('pointer-events', 'none')
            .text(d => d.id);
        
        // Update positions immediately (no animation/force simulation)
        this.updatePositions(nodes, links);
    }
    
    updatePositions(nodes, links) {
        // Create lookup map for node positions
        const nodeMap = new Map();
        nodes.forEach(node => {
            nodeMap.set(node.id, node);
        });
        
        // Update link positions
        this.svg.selectAll('.link')
            .attr('x1', d => {
                const source = nodeMap.get(d.source);
                return source ? source.x : 0;
            })
            .attr('y1', d => {
                const source = nodeMap.get(d.source);
                return source ? source.y : 0;
            })
            .attr('x2', d => {
                const target = nodeMap.get(d.target);
                return target ? target.x : 0;
            })
            .attr('y2', d => {
                const target = nodeMap.get(d.target);
                return target ? target.y : 0;
            });
        
        // Update node positions
        this.svg.selectAll('.node')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        // Update label positions
        this.svg.selectAll('.node-label')
            .attr('x', d => d.x)
            .attr('y', d => d.y);
        
        // Update transmission range positions if they exist
        this.svg.selectAll('.transmission-range')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        // Update node information panel if a node is selected
        if (this.selectedNodes.length > 0) {
            const selectedNodeId = this.selectedNodes[0].id;
            const updatedNode = this.networkData.nodes.find(n => n.id === selectedNodeId);
            if (updatedNode) {
                this.showNodeInfo(updatedNode);
                // Maintain neighbor highlighting
                this.highlightNeighbors(updatedNode);
            }
        }
    }

    showAlert(title, message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <div class="alert-header">
                <strong>${title}</strong>
                <button class="alert-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="alert-message">${message}</div>
        `;
        
        // Add styles if not already added
        if (!document.getElementById('alert-styles')) {
            const style = document.createElement('style');
            style.id = 'alert-styles';
            style.textContent = `
                .alert {
                    position: fixed;
                    top: 80px;
                    right: 20px;
                    max-width: 400px;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    z-index: 1000;
                    margin-bottom: 10px;
                    animation: slideIn 0.3s ease-out;
                }
                .alert-info { background: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460; }
                .alert-warning { background: #fff3cd; border-left: 4px solid #ffc107; color: #856404; }
                .alert-error { background: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
                .alert-success { background: #d4edda; border-left: 4px solid #28a745; color: #155724; }
                .alert-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }
                .alert-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    color: inherit;
                    opacity: 0.7;
                }
                .alert-close:hover { opacity: 1; }
                .alert-message { font-size: 14px; line-height: 1.4; }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Add to body
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 8 seconds for warnings, 5 seconds for others
        const timeout = type === 'warning' ? 8000 : 5000;
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, timeout);
    }

    clearNodePositions() {
        // Clear cached node positions (useful when creating new networks)
        this.nodePositions.clear();
    }

    selectNode(node) {
        // Check if this node is already selected
        const isAlreadySelected = this.selectedNodes.some(n => n.id === node.id);
        
        if (isAlreadySelected) {
            // Deselect the current node
            this.selectedNodes = [];
            // Clear node info when deselecting
            document.getElementById('nodeInfoContent').innerHTML = '<p>Click on a node to see details</p>';
            // Clear neighbor highlighting
            this.clearNeighborHighlighting();
            this.log(`Node ${node.id} deselected`, 'info');
        } else {
            // Clear any previously selected nodes and select this one
            this.selectedNodes = [node];
            // Show node info when selecting
            this.showNodeInfo(node);
            // Highlight neighbors
            this.highlightNeighbors(node);
            this.log(`Node ${node.id} selected`, 'info');
        }
        
        // Update visual selection
        this.svg.selectAll('.node')
            .classed('selected', d => this.selectedNodes.some(n => n.id === d.id));
    }
    
    selectNodeById(nodeId) {
        const node = this.networkData.nodes.find(n => n.id === nodeId);
        if (node) {
            // Clear current selection first
            this.selectedNodes = [];
            this.clearNeighborHighlighting();
            
            // Select the new node
            this.selectNode(node);
        }
    }
    
    highlightNeighbors(selectedNode) {
        // Clear any existing neighbor highlighting
        this.clearNeighborHighlighting();
        
        if (!selectedNode.neighbors) return;
        
        // Highlight neighbor nodes
        this.svg.selectAll('.node')
            .classed('neighbor-highlighted', d => 
                selectedNode.neighbors.includes(d.id) && d.id !== selectedNode.id
            );
        
        // Highlight links to neighbors
        this.svg.selectAll('.link')
            .classed('neighbor-link', d => {
                return (d.source.id === selectedNode.id && selectedNode.neighbors.includes(d.target.id)) ||
                       (d.target.id === selectedNode.id && selectedNode.neighbors.includes(d.source.id));
            });
    }
    
    clearNeighborHighlighting() {
        this.svg.selectAll('.node').classed('neighbor-highlighted', false);
        this.svg.selectAll('.link').classed('neighbor-link', false);
    }
    
    showNodeInfo(node) {
        const content = document.getElementById('nodeInfoContent');
        
        // Calculate total messages
        const totalMessages = (node.message_counts?.hello || 0) + 
                             (node.message_counts?.topology || 0) + 
                             (node.message_counts?.route_discovery || 0) + 
                             (node.message_counts?.data_packets || 0);
        
        // Format neighbors list
        let neighborsHtml = '';
        if (node.neighbors && node.neighbors.length > 0) {
            neighborsHtml = node.neighbors.map(neighborId => {
                const delay = node.neighbor_delays?.[neighborId]?.toFixed(2) || 'N/A';
                return `<div class="neighbor-item clickable" onclick="simulator.selectNodeById(${neighborId})">
                    <span class="neighbor-id">Node ${neighborId}</span>
                    <span class="neighbor-delay">Delay: ${delay}</span>
                </div>`;
            }).join('');
        } else {
            neighborsHtml = '<div class="no-neighbors">No connected neighbors</div>';
        }
        
        content.innerHTML = `
            <div class="node-info-details">
                <h5>🔌 Node ${node.id}</h5>
                
                <div class="info-section">
                    <h6>📍 Location & Network</h6>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Position:</span>
                            <span class="info-value">(${node.x?.toFixed(2) || 0}, ${node.y?.toFixed(2) || 0})</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Range:</span>
                            <span class="info-value">${node.transmission_range?.toFixed(2) || 0}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Connections:</span>
                            <span class="info-value">${node.connections || 0}</span>
                        </div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h6>🔗 Connected Neighbors</h6>
                    <div class="neighbors-list">
                        ${neighborsHtml}
                    </div>
                </div>
                
                <div class="info-section">
                    <h6>📊 Message Statistics</h6>
                    <div class="message-stats">
                        <div class="stat-bar">
                            <span class="stat-label">Hello Messages:</span>
                            <span class="stat-value">${node.message_counts?.hello || 0}</span>
                        </div>
                        <div class="stat-bar">
                            <span class="stat-label">Topology Messages:</span>
                            <span class="stat-value">${node.message_counts?.topology || 0}</span>
                        </div>
                        <div class="stat-bar">
                            <span class="stat-label">Route Discovery:</span>
                            <span class="stat-value">${node.message_counts?.route_discovery || 0}</span>
                        </div>
                        <div class="stat-bar">
                            <span class="stat-label">Data Packets:</span>
                            <span class="stat-value">${node.message_counts?.data_packets || 0}</span>
                        </div>
                        <div class="stat-bar total">
                            <span class="stat-label"><strong>Total Messages:</strong></span>
                            <span class="stat-value"><strong>${totalMessages}</strong></span>
                        </div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h6>🔍 Actions</h6>
                    <button class="btn btn-small btn-routing" onclick="simulator.getRoutingInfo([${node.id}])">
                        📋 Show Routing Table
                    </button>
                </div>
            </div>
        `;
    }
    
    getRoutingInfo(nodeIds) {
        this.socket.emit('get_routing_info', { node_ids: nodeIds });
    }
    
    showRoutingInfo(data) {
        const modal = document.getElementById('routingModal');
        const content = document.getElementById('routingContent');
        
        let html = '';
        for (const [nodeId, info] of Object.entries(data)) {
            html += `
                <div class="routing-node-info">
                    <h4>Node ${nodeId}</h4>
                    <div class="routing-tables">
                        <div class="routing-table">
                            <h5>Routing Table</h5>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr style="background: #f8f9fa;">
                                    <th style="border: 1px solid #ddd; padding: 8px;">Destination</th>
                                    <th style="border: 1px solid #ddd; padding: 8px;">Next Hop</th>
                                    <th style="border: 1px solid #ddd; padding: 8px;">Cost</th>
                                </tr>
            `;
            
            for (const [dest, route] of Object.entries(info.routing_table)) {
                const nextHop = route[0];
                const cost = route[1];
                html += `
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">${dest}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${nextHop}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${cost === Infinity ? '∞' : cost.toFixed(3)}</td>
                    </tr>
                `;
            }
            
            html += `
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }
        
        content.innerHTML = html;
        modal.style.display = 'block';
    }
    
    updateNodeSelects() {
        const selects = ['nodeA', 'nodeB'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (!select) return; // Skip if element doesn't exist
            
            select.innerHTML = '';
            
            this.networkData.nodes.forEach(node => {
                const option = document.createElement('option');
                option.value = node.id;
                option.textContent = `Node ${node.id}`;
                select.appendChild(option);
            });
        });
    }
    
    updateStatistics(stats) {
        document.getElementById('statRequests').textContent = stats.requests || 0;
        document.getElementById('statSuccessful').textContent = stats.successful_transmissions || 0;
        document.getElementById('statFailed').textContent = stats.failed_transmissions || 0;
        
        const successRate = stats.requests > 0 ? 
            ((stats.successful_transmissions || 0) / stats.requests * 100).toFixed(1) : '0';
        document.getElementById('statSuccessRate').textContent = `${successRate}%`;
        
        const avgDelay = stats.successful_transmissions > 0 ? 
            ((stats.total_delay || 0) / stats.successful_transmissions).toFixed(3) : '0.000';
        document.getElementById('statAvgDelay').textContent = avgDelay;
        
        document.getElementById('statLinksAdded').textContent = stats.links_added || 0;
        document.getElementById('statLinksRemoved').textContent = stats.links_removed || 0;
    }
    
    updateSimulationState(state) {
        document.getElementById('currentStep').textContent = state.current_step;
        document.getElementById('maxSteps').textContent = state.max_steps;
        document.getElementById('gotoStep').max = state.max_steps;
        
        // Update button states
        document.getElementById('stepSimulation').disabled = !state.has_network;
        document.getElementById('addLink').disabled = !state.has_network;
        document.getElementById('removeLink').disabled = !state.has_network;
        
        document.getElementById('prevStep').disabled = state.current_step <= 0;
        document.getElementById('nextStep').disabled = state.current_step >= state.max_steps;
        document.getElementById('firstStep').disabled = state.current_step <= 0;
        document.getElementById('lastStep').disabled = state.current_step >= state.max_steps;
    }
    
    updateConnectionStatus(text, connected) {
        document.getElementById('connectionText').textContent = text;
        const indicator = document.getElementById('connectionStatus');
        indicator.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
    }
    
    zoom(factor) {
        this.svg.transition().duration(300).call(
            d3.zoom().transform,
            this.transform.scale(factor)
        );
    }
    
    resetZoom() {
        this.svg.transition().duration(500).call(
            d3.zoom().transform,
            d3.zoomIdentity
        );
    }
    
    toggleLabels(show) {
        this.svg.selectAll('.node-label').style('display', show ? 'block' : 'none');
    }
    
    toggleTransmissionRanges(show) {
        if (show) {
            const ranges = this.svg.select('.transmission-ranges')
                .selectAll('.transmission-range')
                .data(this.networkData.nodes, d => d.id);
            
            ranges.enter()
                .append('circle')
                .attr('class', 'transmission-range')
                .attr('r', d => d.transmission_range * 30) // Scale for visualization
                .style('fill', 'none')
                .style('stroke', '#3498db')
                .style('stroke-width', 1)
                .style('stroke-dasharray', '5,5')
                .style('opacity', 0.3);
        } else {
            this.svg.selectAll('.transmission-range').remove();
        }
    }
    
    showExportModal(data) {
        const modal = document.getElementById('exportModal');
        const content = document.getElementById('exportContent');
        
        if (data.type === 'json') {
            content.innerHTML = `
                <h4>JSON Export</h4>
                <textarea style="width: 100%; height: 300px; font-family: monospace;" readonly>${JSON.stringify(data.data, null, 2)}</textarea>
            `;
        } else if (data.type === 'report') {
            content.innerHTML = `
                <h4>Simulation Report</h4>
                <pre style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">${data.data}</pre>
            `;
        }
        
        document.getElementById('downloadExport').onclick = () => {
            const blob = new Blob([data.type === 'json' ? JSON.stringify(data.data, null, 2) : data.data], 
                                { type: data.type === 'json' ? 'application/json' : 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            URL.revokeObjectURL(url);
        };
        
        modal.style.display = 'block';
    }
    
    log(message, type = 'info') {
        const logContainer = document.getElementById('eventLog');
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 100 entries
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    clearLog() {
        document.getElementById('eventLog').innerHTML = '';
        this.log('Log cleared', 'info');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.simulator = new NetworkSimulator();
});
