import networkx as nx
import time
from typing import List, Tuple, Dict, Any, Optional, Iterator, Set, Callable
from collections import defaultdict

from .base import BaseGraph
from .flow.decomposition import decompose_flow, simplify_paths
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__,logging.INFO)

class NetworkXGraph(BaseGraph):
    def __init__(self, edges: List[Tuple[str, str]], capacities: List[float], tokens: List[str]):
        self.g_nx = self._create_graph(edges, capacities, tokens)
        self.logger = logger

    def _create_graph(self, edges: List[Tuple[str, str]], capacities: List[float], 
                     tokens: List[str]) -> nx.DiGraph:
        """Create NetworkX graph with edge properties."""
        g = nx.DiGraph()
        
        # Add all edges in a single batch with their properties
        edge_data = [
            (u, v, {'capacity': int(capacity), 'label': token}) 
            for (u, v), capacity, token in zip(edges, capacities, tokens)
        ]
        g.add_edges_from(edge_data)
        
        return g

    def compute_flow(self, source: str, sink: str, flow_func: Optional[Callable] = None,
                    requested_flow: Optional[str] = None) -> Tuple[int, Dict[str, Dict[str, int]]]:
        """Compute maximum flow between source and sink nodes."""
        if flow_func is None:
            flow_func = nx.algorithms.flow.preflow_push

        # Early exit if sink has no incoming edges
        if self.g_nx.in_degree(sink) == 0:
            logger.debug("Sink has no incoming edges. No flow is possible.")
            return 0, {}

        # Create a copy of the graph for modification
        graph_copy = self.g_nx.copy()
        
        # Process direct edges efficiently
        direct_flow = 0
        direct_flow_dict = {}
        direct_edges = []
        
        # Collect all potential direct edges first
        for node in graph_copy.successors(source):
            if '_' in node and sink in graph_copy.successors(node):
                capacity_source_intermediate = graph_copy[source][node]['capacity']
                capacity_intermediate_sink = graph_copy[node][sink]['capacity']
                direct_edges.append((node, min(capacity_source_intermediate, capacity_intermediate_sink)))

        # Process direct edges if any exist
        if direct_edges:
            direct_edges.sort(key=lambda x: x[1], reverse=True)
            req_flow_int = int(requested_flow) if requested_flow is not None else None
            remaining_flow = req_flow_int if req_flow_int is not None else float('inf')
            
            for intermediate_node, capacity in direct_edges:
                if req_flow_int is not None and remaining_flow <= 0:
                    break
                    
                flow = min(capacity, remaining_flow) if req_flow_int is not None else capacity
                
                if flow > 0:
                    direct_flow_dict.setdefault(source, {})[intermediate_node] = flow
                    direct_flow_dict.setdefault(intermediate_node, {})[sink] = flow
                    direct_flow += flow
                    
                    # Update remaining capacities
                    graph_copy[source][intermediate_node]['capacity'] -= flow
                    graph_copy[intermediate_node][sink]['capacity'] -= flow
                    
                    if req_flow_int is not None:
                        remaining_flow -= flow

            # Early return if direct edges satisfy requested flow
            if req_flow_int is not None and direct_flow >= req_flow_int:
                logger.debug(f"Satisfied requested flow of {requested_flow} with direct edges.")
                self._flow_dict = direct_flow_dict  # Cache the flow dictionary
                return direct_flow, direct_flow_dict

        # Calculate remaining requested flow
        remaining_requested_flow = None if requested_flow is None else int(requested_flow) - direct_flow

        try:
            # Remove edges with zero capacity
            zero_capacity_edges = [(u, v) for u, v, d in graph_copy.edges(data=True) 
                                if d['capacity'] <= 0]
            graph_copy.remove_edges_from(zero_capacity_edges)
            
            start = time.time()
            # Compute the maximum flow
            try:
                flow_value, flow_dict = nx.maximum_flow(
                    graph_copy, source, sink,
                    flow_func=flow_func,
                    cutoff=remaining_requested_flow
                )
            except:
                flow_value, flow_dict = nx.maximum_flow(
                    graph_copy, source, sink,
                    flow_func=flow_func
                )
            logger.debug(f"Solver Time: {time.time() - start}")

            # Convert values to integers and remove zero flows
            flow_dict = {
                u: {v: int(f) for v, f in flows.items() if f > 0}
                for u, flows in flow_dict.items()
            }
            flow_value = int(flow_value)

            # Combine with direct flows if any
            if direct_flow_dict:
                for u, flows in direct_flow_dict.items():
                    if u not in flow_dict:
                        flow_dict[u] = flows.copy()
                    else:
                        for v, f in flows.items():
                            flow_dict[u][v] = flow_dict[u].get(v, 0) + f

            # Cache the flow dictionary
            self._flow_dict = flow_dict
            return flow_value + direct_flow, flow_dict

        except Exception as e:
            logger.error(f"Error in flow computation: {str(e)}")
            raise

    def flow_decomposition(self, flow_dict: Dict[str, Dict[str, int]], source: str, sink: str,
                          requested_flow: Optional[int] = None) -> Tuple[List[Tuple[List[str], List[str], int]],
                                                                       Dict[Tuple[str, str], int]]:
        """Decompose flow into paths."""
        # Use cached flow dictionary if available
        flow_dict = getattr(self, '_flow_dict', flow_dict)
        paths, edge_flows = decompose_flow(flow_dict, source, sink, requested_flow)
        
        # Add labels for NetworkX implementation
        labeled_paths = []
        for path, _, flow in paths:
            path_labels = []
            for u, v in zip(path[:-1], path[1:]):
                edge_data = self.get_edge_data(u, v)
                path_labels.append(edge_data.get('label', 'no_label'))
            labeled_paths.append((path, path_labels, flow))
        
        return labeled_paths, edge_flows

    def simplified_flow_decomposition(self, original_paths: List[Tuple[List[str], List[str], int]]) -> List[Tuple[List[str], List[str], int]]:
        """Create simplified paths."""
        return simplify_paths(original_paths)

    # Required BaseGraph interface methods
    def num_vertices(self) -> int:
        return self.g_nx.number_of_nodes()
    
    def num_edges(self) -> int:
        return self.g_nx.number_of_edges()
    
    def get_vertices(self) -> Set[str]:
        return set(self.g_nx.nodes())
    
    def get_edges(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        return [(u, v, d) for u, v, d in self.g_nx.edges(data=True)]
    
    def in_degree(self, vertex_id: str) -> int:
        return self.g_nx.in_degree(vertex_id)
    
    def out_degree(self, vertex_id: str) -> int:
        return self.g_nx.out_degree(vertex_id)
    
    def degree(self, vertex_id: str) -> int:
        return self.g_nx.degree(vertex_id)
    
    def predecessors(self, vertex_id: str) -> Iterator[str]:
        return self.g_nx.predecessors(vertex_id)
    
    def successors(self, vertex_id: str) -> Iterator[str]:
        return self.g_nx.successors(vertex_id)
    
    def has_vertex(self, vertex_id: str) -> bool:
        return vertex_id in self.g_nx
    
    def has_edge(self, u: str, v: str) -> bool:
        return self.g_nx.has_edge(u, v)
    
    def get_edge_data(self, u: str, v: str) -> Dict[str, Any]:
        return self.g_nx.get_edge_data(u, v) or {}
    
    def get_edge_capacity(self, u: str, v: str) -> Optional[int]:
        if self.has_edge(u, v):
            return self.g_nx[u][v].get('capacity')
        return None

    def get_node_outflow_capacity(self, source_id: str) -> int:
        total_capacity = 0
        if source_id not in self.g_nx:
            return total_capacity
        for neighbor in self.g_nx.successors(source_id):
            if '_' in neighbor:
                edge_data = self.g_nx.get_edge_data(source_id, neighbor)
                capacity = edge_data.get('capacity', 0)
                total_capacity += capacity
        return total_capacity

    def get_node_inflow_capacity(self, sink_id: str) -> int:
        total_capacity = 0
        if sink_id not in self.g_nx:
            return total_capacity
        for predecessor in self.g_nx.predecessors(sink_id):
            if '_' in predecessor:
                edge_data = self.g_nx.get_edge_data(predecessor, sink_id)
                capacity = edge_data.get('capacity', 0)
                total_capacity += capacity
        return total_capacity
    

    def prepare_arbitrage_graph(self, start_node: str, start_token: str, end_token: str) -> Tuple[str, str]:
        """
        Prepare graph for arbitrage analysis by modifying only outgoing edges from source.
        
        Args:
            start_node: The actual source node ID
            start_token: The token ID to start with 
            end_token: The token ID to end with
        """
        try:
            # Verify start intermediate node exists
            start_intermediate = f"{start_node}_{start_token}"
            if not self.has_vertex(start_intermediate):
                self.logger.warning(f"No intermediate node found for {start_node} with token {start_token}")
                return None, None

            # Store outgoing edges in a list before modifying graph
            self._temp_edges = []
            outgoing_edges = [(u, v, d) for u, v, d in self.g_nx.out_edges(start_node, data=True)]
            for (u, v, data) in outgoing_edges:
                self._temp_edges.append((u, v, data.copy()))
                self.g_nx.remove_edge(u, v)

            # Add back only the edge to start token intermediate node
            edge_data = next((data for _, v, data in self._temp_edges if v == start_intermediate), None)
            if edge_data is None:
                self.logger.warning(f"No edge found from {start_node} to {start_intermediate}")
                self._restore_edges()
                return None, None

            # Add the single allowed outgoing edge
            self.g_nx.add_edge(start_node, start_intermediate, **edge_data)
            available_capacity = edge_data['capacity']
            self.logger.debug(f"Capacity from {start_node} to {start_intermediate}: {available_capacity}")

            # Create virtual sink with unique ID
            virtual_sink = f"virtual_sink_{start_node}_{start_token}_{end_token}"
            self.g_nx.add_node(virtual_sink)

            # Find and store potential end nodes before adding edges
            end_positions = []
            for u, v, data in list(self.g_nx.edges(data=True)):
                if v == start_node and '_' in u:
                    holder, token = u.split('_')
                    if token == end_token:
                        end_positions.append((u, data.get('capacity', 0)))

            # Add edges to virtual sink
            edges_added = 0
            for position, capacity in end_positions:
                # Capacity limited by both return edge capacity and initial capacity
                limited_capacity = min(capacity, available_capacity)
                self.g_nx.add_edge(
                    position,
                    virtual_sink,
                    capacity=limited_capacity,
                    label=end_token,
                    is_virtual=True
                )
                edges_added += 1

            if edges_added == 0:
                self.logger.warning("No valid end states found for arbitrage")
                self._restore_edges()
                return None, None

            self.logger.debug(f"Added {edges_added} edges to virtual sink")
            return start_node, virtual_sink

        except Exception as e:
            self.logger.error(f"Error preparing arbitrage graph: {e}")
            self._restore_edges()
            raise

    def _restore_edges(self):
        """Restore temporarily removed edges."""
        try:
            if hasattr(self, '_temp_edges'):
                for u, v, data in self._temp_edges:
                    self.g_nx.add_edge(u, v, **data)
                delattr(self, '_temp_edges')
        except Exception as e:
            self.logger.error(f"Error restoring edges: {e}")
            raise

    def find_arbitrage(self, start_node: str, start_token: str, end_token: str,
                  flow_func: Optional[Callable] = None) -> Tuple[int, List[Tuple[List[str], List[str], int]]]:
        """Find arbitrage opportunities between tokens."""
        try:
            # Prepare graph for arbitrage
            source, virtual_sink = self.prepare_arbitrage_graph(
                start_node, start_token, end_token
            )
            
            if source is None or virtual_sink is None:
                return 0, [], {}, {}

            # Compute maximum flow
            flow_value, flow_dict = self.compute_flow(
                source,
                virtual_sink,
                flow_func=flow_func
            )

            if flow_value == 0:
                return 0, []

            # Convert virtual sink flows to actual flows
            real_flow_dict = self.interpret_arbitrage_flow(flow_dict, start_node, virtual_sink)
            
            # Find all cycles in the flow
            cycles = []
            residual_flows = defaultdict(dict)
            
            # Initialize residual flows
            for u, flows in real_flow_dict.items():
                for v, f in flows.items():
                    if f > 0:
                        residual_flows[u][v] = f
            
            # Find cycles using DFS from the start node
            def find_cycle_dfs(node, path, visited, cycle_flow):
                if len(path) > 1 and node == start_node:
                    # Found a cycle
                    cycles.append((path[:], cycle_flow))
                    return
                    
                for next_node, flow in residual_flows[node].items():
                    if flow > 0 and (next_node not in visited or next_node == start_node):
                        new_flow = min(cycle_flow, flow)
                        path.append(next_node)
                        visited.add(next_node)
                        find_cycle_dfs(next_node, path, visited, new_flow)
                        visited.remove(next_node)
                        path.pop()
            
            # Start cycle finding from start_node
            start_id = f"{start_node}_{start_token}"
            find_cycle_dfs(start_id, [start_id], {start_id}, float('inf'))
            
            # Convert cycles to the expected format
            formatted_paths = []
            edge_flows = {}
            
            for cycle, flow in cycles:
                # Extract tokens from intermediate nodes
                tokens = []
                for node in cycle[1:]:  # Skip first node as it's already included
                    if '_' in node:
                        _, token = node.split('_')
                        tokens.append(token)
                        
                formatted_paths.append((cycle, tokens, flow))
                
                # Record edge flows
                for i in range(len(cycle) - 1):
                    edge = (cycle[i], cycle[i + 1])
                    edge_flows[edge] = edge_flows.get(edge, 0) + flow

            return flow_value, formatted_paths, edge_flows

        except Exception as e:
            self.logger.error(f"Error finding arbitrage: {e}")
            raise
        finally:
            # Clean up
            self.cleanup_arbitrage_graph()

    def interpret_arbitrage_flow(self, flow_dict: Dict[str, Dict[str, int]], 
                           start_node: str, virtual_sink: str) -> Dict[str, Dict[str, int]]:
        """Convert flows through virtual sink back to actual token flows."""
        real_flows = defaultdict(dict)
        
        # First copy all non-virtual flows
        for u, flows in flow_dict.items():
            for v, flow in flows.items():
                if v != virtual_sink and flow > 0:
                    real_flows[u][v] = flow
        
        # Process flows to virtual sink
        for u, flows in flow_dict.items():
            virtual_flow = flows.get(virtual_sink, 0)
            if virtual_flow > 0:
                # Get capacity of edge from u back to start_node
                back_edge_capacity = self.get_edge_capacity(u, start_node)
                if back_edge_capacity is not None:
                    # Add the return flow
                    real_flows[u][start_node] = virtual_flow
        
        return dict(real_flows)

    def cleanup_arbitrage_graph(self):
        """Remove all virtual nodes and edges used for arbitrage analysis."""
        try:
            # Make a list of edges to remove before modifying graph
            virtual_edges = [
                (u, v) for u, v, data in list(self.g_nx.edges(data=True))
                if data.get('is_virtual', False)
            ]
            self.g_nx.remove_edges_from(virtual_edges)
            
            # Make a list of nodes to remove before modifying graph
            virtual_nodes = [
                node for node in list(self.g_nx.nodes())
                if str(node).startswith('virtual_sink_')
            ]
            self.g_nx.remove_nodes_from(virtual_nodes)
            
            # Restore original edges if needed
            if hasattr(self, '_temp_edges'):
                self._restore_edges()
                
        except Exception as e:
            self.logger.error(f"Error cleaning up arbitrage graph: {e}")
            raise