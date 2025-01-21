from typing import Dict, List, Tuple, Optional
from .utils import find_flow_path, update_residual_graph

def decompose_flow(flow_dict: Dict[str, Dict[str, int]], source: str, sink: str,
                  requested_flow: Optional[int] = None) -> Tuple[List[Tuple[List[str], List[str], int]], 
                                                              Dict[Tuple[str, str], int]]:
    """Decompose a flow into paths."""
    paths = []
    edge_flows = {}
    current_flow = 0
    
    # Build residual flow graph
    residual_flow = {u: dict(flows) for u, flows in flow_dict.items()}
    
    while True:
        # Find a path from source to sink with positive flow
        path = find_flow_path(residual_flow, source, sink)
        if not path:
            break
        
        # Calculate path flow
        path_flow = min(residual_flow[u][v] for u, v in zip(path[:-1], path[1:]))
        
        # Apply flow limit if requested
        if requested_flow is not None:
            remaining_flow = requested_flow - current_flow
            if remaining_flow <= 0:
                break
            path_flow = min(path_flow, remaining_flow)
        
        # Update flows
        for u, v in zip(path[:-1], path[1:]):
            edge_flows[(u, v)] = edge_flows.get((u, v), 0) + path_flow
        
        # Update residual graph
        update_residual_graph(residual_flow, path, path_flow)
        
        paths.append((path, [], path_flow))
        current_flow += path_flow
        
        if requested_flow is not None and current_flow >= requested_flow:
            break
    
    return paths, edge_flows

def simplify_paths(original_paths: List[Tuple[List[str], List[str], int]]) -> List[Tuple[List[str], List[str], int]]:
    """Simplify paths by removing intermediate nodes while preserving key transitions."""
    simplified_paths = []
    
    for path, tokens, flow in original_paths:
        simplified_path = []
        simplified_tokens = []
        
        # Start with source
        simplified_path.append(path[0])
        
        # Process middle nodes - keep real nodes where token changes occur
        prev_token = None
        for i, node in enumerate(path[1:-1]): 
            if '_' in node:
                # Get token from intermediate node
                _, token = node.split('_')
                if token != prev_token:
                    # Keep the real node before token change
                    real_node = node.split('_')[0]
                    if not simplified_path or simplified_path[-1] != real_node:
                        simplified_path.append(real_node)
                        if prev_token:
                            simplified_tokens.append(prev_token)
                    prev_token = token
                    
            else:
                # This is a real node - keep it if it represents a transition
                if prev_token:
                    simplified_path.append(node)
                    simplified_tokens.append(prev_token)
                    prev_token = None
        
        # Add final token
        if prev_token:
            simplified_tokens.append(prev_token)
            
        # Complete cycle back to source
        simplified_path.append(path[0])
        
        # Only add if path has meaningful transitions
        if len(simplified_path) > 2 and len(simplified_tokens) > 0:
            simplified_paths.append((simplified_path, simplified_tokens, flow))
    
    return simplified_paths


__all__ = ['decompose_flow', 'simplify_paths']