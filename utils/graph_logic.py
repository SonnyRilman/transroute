import networkx as nx
from haversine import haversine, Unit

def build_graph(nodes, edges):
    """
    Build NetworkX Graph from parsed KML nodes and edges.
    Calculate weights using Haversine distance (in KM).
    """
    G = nx.Graph()
    
    # Add nodes with lat, lon attributes
    for node_id, coords in nodes.items():
        G.add_node(node_id, pos=coords)
        
    # Naive matching: match edge coordinates to closest explicitly defined nodes
    # For a robust implementation, the LineString endpoints should exactly match the Node coordinates
    for edge in edges:
        coords = edge['coordinates']
        if len(coords) >= 2:
            start_coord = coords[0]
            end_coord = coords[-1]
            
            # Find closest defined nodes to these coordinates
            start_node = find_nearest_node(start_coord, nodes)
            end_node = find_nearest_node(end_coord, nodes)
            
            if start_node and end_node and start_node != end_node:
                # Calculate True Distance for the weight
                dist = haversine(start_coord, end_coord, unit=Unit.KILOMETERS)
                G.add_edge(start_node, end_node, weight=dist, path=coords)
                
    return G

def find_nearest_node(target_coords, nodes_dict):
    """
    Find the nearest node from a dictionary of nodes to a target coordinate (lat, lon)
    """
    min_dist = float('inf')
    nearest_node = None
    
    for node_name, node_coords in nodes_dict.items():
        dist = haversine(target_coords, node_coords, unit=Unit.KILOMETERS)
        if dist < min_dist:
            min_dist = dist
            nearest_node = node_name
            
    return nearest_node

def find_shortest_path(G, start_node, end_node):
    """
    Execute Dijkstra's algorithm to find the shortest path.
    Returns: (path_list, total_distance)
    """
    try:
        path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
        distance = nx.shortest_path_length(G, source=start_node, target=end_node, weight='weight')
        return path, distance
    except nx.NetworkXNoPath:
        return None, float('inf')
    except nx.NodeNotFound:
        return None, float('inf')
