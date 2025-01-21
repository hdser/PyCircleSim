from typing import Dict, List, Tuple, Optional
from collections import deque

def find_flow_path(flow_dict: Dict[str, Dict[str, int]], source: str, sink: str) -> List[str]:
    """Find a path with positive flow using iterative DFS."""
    visited = {source}
    path = [source]
    stack = [(source, iter(flow_dict.get(source, {}).items()))]
    
    while stack:
        current, edges = stack[-1]
        try:
            next_node, flow = next(edges)
            if flow > 0 and next_node not in visited:
                if next_node == sink:
                    path.append(next_node)
                    return path
                visited.add(next_node)
                path.append(next_node)
                stack.append((next_node, iter(flow_dict.get(next_node, {}).items())))
        except StopIteration:
            stack.pop()
            if path:
                path.pop()
    
    return []

def update_residual_graph(residual_flow: Dict[str, Dict[str, int]], path: List[str], 
                         path_flow: int) -> None:
    """Update residual graph after finding a path."""
    for u, v in zip(path[:-1], path[1:]):
        residual_flow[u][v] -= path_flow
        if residual_flow[u][v] == 0:
            del residual_flow[u][v]
        if not residual_flow[u]:
            del residual_flow[u]

def verify_flow_conservation(flow_dict: Dict[str, Dict[str, int]], source: str, sink: str) -> bool:
    """Verify flow conservation at intermediate nodes."""
    for node in flow_dict:
        if node not in (source, sink):
            in_flow = sum(flows.get(node, 0) for flows in flow_dict.values())
            out_flow = sum(flow_dict.get(node, {}).values())
            if abs(in_flow - out_flow) > 1e-10:  # Allow for small numerical errors
                return False
    return True

def calculate_flow_metrics(paths: List[Tuple[List[str], List[str], int]],
                         edge_flows: Dict[Tuple[str, str], int]) -> Dict[str, float]:
    """Calculate flow metrics."""
    if not paths:
        return {
            'total_flow': 0,
            'average_path_flow': 0,
            'max_path_flow': 0,
            'min_path_flow': 0,
            'unique_edges': 0,
            'average_edge_flow': 0,
        }

    flows = [flow for _, _, flow in paths]
    total_flow = sum(flows)
    
    metrics = {
        'total_flow': total_flow,
        'average_path_flow': total_flow / len(paths),
        'max_path_flow': max(flows),
        'min_path_flow': min(flows),
        'unique_edges': len(edge_flows),
        'average_edge_flow': total_flow / len(edge_flows) if edge_flows else 0,
    }
    
    # Add path length statistics
    path_lengths = [len(path) for path, _, _ in paths]
    metrics.update({
        'average_path_length': sum(path_lengths) / len(path_lengths),
        'max_path_length': max(path_lengths),
        'min_path_length': min(path_lengths),
    })
    
    return metrics

def find_augmenting_path_bfs(residual_flow: Dict[str, Dict[str, int]], 
                           source: str, sink: str) -> Tuple[List[str], int]:
    """Find augmenting path using BFS."""
    queue = deque([(source, [source], float('inf'))])
    visited = {source}

    while queue:
        node, path, flow = queue.popleft()
        if node == sink:
            return path, flow
        for next_node, edge_flow in residual_flow.get(node, {}).items():
            if edge_flow > 0 and next_node not in visited:
                visited.add(next_node)
                new_flow = min(flow, edge_flow)
                queue.append((next_node, path + [next_node], new_flow))
    return [], 0