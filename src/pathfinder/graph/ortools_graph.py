from ortools.graph.python import max_flow
import time
from typing import List, Tuple, Dict, Any, Optional, Iterator, Set, Callable
from collections import defaultdict

from .base import BaseGraph
from .flow.decomposition import decompose_flow, simplify_paths
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__,logging.INFO)

class ORToolsGraph(BaseGraph):
    def __init__(self, edges: List[Tuple[str, str]], capacities: List[float], tokens: List[str]):
        """
        Initialize OR-Tools graph implementation.
        
        Args:
            edges: List of (source, target) node pairs
            capacities: List of edge capacities
            tokens: List of token identifiers for each edge
        """
        self.logger = logger
        # Create mappings and data structures
        self._initialize_data_structures(edges, capacities, tokens)
        
        # Initialize OR-Tools solver
        self.solver = max_flow.SimpleMaxFlow()
        
        # Create adjacency maps for efficient lookups
        self.arc_adjacency = {}  # node_idx -> List[(arc_idx, head_idx, capacity)]
        self.reverse_arc_adjacency = {}  # node_idx -> List[(arc_idx, tail_idx, capacity)]
        
        # Initialize solver with edges
        self._initialize_solver()

    def _initialize_data_structures(self, edges: List[Tuple[str, str]], 
                                 capacities: List[float], tokens: List[str]):
        """Initialize internal data structures."""
        # Create node index mappings
        unique_nodes = set()
        for u, v in edges:
            unique_nodes.add(u)
            unique_nodes.add(v)
        self.node_to_index = {node: idx for idx, node in enumerate(sorted(unique_nodes))}
        self.index_to_node = {idx: node for node, idx in self.node_to_index.items()}

        # Store edge data
        self.edges = []
        self.edge_data = {}  # (u, v) -> {capacity, label}
        self.outgoing_edges = defaultdict(list)  # node -> [(neighbor, capacity, label)]
        self.incoming_edges = defaultdict(list)  # node -> [(neighbor, capacity, label)]

        for (u, v), capacity, token in zip(edges, capacities, tokens):
            self.edges.append((u, v))
            self.edge_data[(u, v)] = {
                'capacity': int(capacity),
                'label': token
            }
            self.outgoing_edges[u].append((v, int(capacity), token))
            self.incoming_edges[v].append((u, int(capacity), token))

    def _initialize_solver(self):
        """Initialize OR-Tools solver with edges."""
        for u, v in self.edges:
            u_idx = self.node_to_index[u]
            v_idx = self.node_to_index[v]
            capacity = self.edge_data[(u, v)]['capacity']
            
            # Add edge to solver
            arc_idx = self.solver.add_arc_with_capacity(u_idx, v_idx, capacity)
            
            # Build forward adjacency
            if u_idx not in self.arc_adjacency:
                self.arc_adjacency[u_idx] = []
            self.arc_adjacency[u_idx].append((arc_idx, v_idx, capacity))
            
            # Build reverse adjacency
            if v_idx not in self.reverse_arc_adjacency:
                self.reverse_arc_adjacency[v_idx] = []
            self.reverse_arc_adjacency[v_idx].append((arc_idx, u_idx, capacity))

    def compute_flow(self, source: str, sink: str, flow_func: Optional[Callable] = None,
                requested_flow: Optional[str] = None) -> Tuple[int, Dict[str, Dict[str, int]]]:
        """
        Compute maximum flow between source and sink nodes using OR-Tools.
        Note: flow_func parameter is ignored as OR-Tools uses its own algorithm.
        """
        if not self.has_vertex(source) or not self.has_vertex(sink):
            raise ValueError(f"Source node '{source}' or sink node '{sink}' not in graph.")
                
        source_idx = self.node_to_index[source]
        sink_idx = self.node_to_index[sink]
        
        if self.solver.num_arcs() == 0:
            logger.debug("No edges in graph. No flow is possible.")
            return 0, {}

        # Store original capacities for direct paths before processing
        modified_edges = []
        source_edges = self.arc_adjacency.get(source_idx, [])
        for src_arc_idx, intermediate_idx, _ in source_edges:
            intermediate_node = self.index_to_node[intermediate_idx]
            if '_' in intermediate_node:
                sink_edges = self.arc_adjacency.get(intermediate_idx, [])
                for sink_arc_idx, target_idx, _ in sink_edges:
                    if target_idx == sink_idx:
                        modified_edges.extend([
                            (src_arc_idx, self.solver.capacity(src_arc_idx)),
                            (sink_arc_idx, self.solver.capacity(sink_arc_idx))
                        ])

        # Process direct paths efficiently using cached adjacency maps
        direct_flow, direct_flow_dict = self._process_direct_paths(
            source, sink, source_idx, sink_idx, requested_flow
        )

        # Restore original capacities
        for arc_idx, original_capacity in modified_edges:
            self.solver.set_arc_capacity(arc_idx, original_capacity)

        if requested_flow and direct_flow >= int(requested_flow):
            logger.debug(f"Satisfied requested flow of {requested_flow} with direct edges.")
            return direct_flow, direct_flow_dict

        remaining_flow = None if requested_flow is None else int(requested_flow) - direct_flow

        # Solve max flow
        start_time = time.time()
        status = self.solver.solve(source_idx, sink_idx)
        logger.debug(f"Solver Time: {time.time() - start_time}")

        if status == self.solver.OPTIMAL:
            total_flow, flow_dict = self._build_flow_dict(
                sink_idx, remaining_flow, direct_flow_dict
            )
            # Store the flow dictionary to avoid recomputation
            self._flow_dict = flow_dict
            return total_flow + direct_flow, flow_dict
        else:
            raise RuntimeError("OR-Tools solver failed to find optimal solution")
    

    def _process_direct_paths(self, source: str, sink: str, source_idx: int, sink_idx: int,
                            requested_flow: Optional[str]) -> Tuple[int, Dict[str, Dict[str, int]]]:
        """Process direct paths through intermediate nodes efficiently."""
        direct_flow = 0
        direct_flow_dict = {}
        max_flow = float('inf') if requested_flow is None else int(requested_flow)
        
        # Use cached adjacency maps
        source_edges = self.arc_adjacency.get(source_idx, [])
        for src_arc_idx, intermediate_idx, source_capacity in source_edges:
            intermediate_node = self.index_to_node[intermediate_idx]
            
            if '_' in intermediate_node:
                sink_edges = self.arc_adjacency.get(intermediate_idx, [])
                for sink_arc_idx, target_idx, sink_capacity in sink_edges:
                    if target_idx == sink_idx:
                        # Calculate flow through this path
                        current_source_cap = self.solver.capacity(src_arc_idx)
                        current_sink_cap = self.solver.capacity(sink_arc_idx)
                        flow = min(current_source_cap, current_sink_cap, max_flow - direct_flow)
                        
                        if flow > 0:
                            # Update capacities in solver
                            self.solver.set_arc_capacity(src_arc_idx, current_source_cap - flow)
                            self.solver.set_arc_capacity(sink_arc_idx, current_sink_cap - flow)
                            
                            # Record the flow
                            direct_flow_dict.setdefault(source, {})[intermediate_node] = flow
                            direct_flow_dict.setdefault(intermediate_node, {})[sink] = flow
                            direct_flow += flow
                            
                            if direct_flow >= max_flow:
                                return direct_flow, direct_flow_dict
                        break

        return direct_flow, direct_flow_dict

    def _build_flow_dict(self, sink_idx: int, remaining_flow: Optional[int],
                        direct_flow_dict: Dict[str, Dict[str, int]]) -> Tuple[int, Dict[str, Dict[str, int]]]:
        """Build flow dictionary from solver results."""
        flow_value = int(self.solver.optimal_flow())
        if remaining_flow is not None:
            flow_value = min(flow_value, remaining_flow)

        flow_dict = {}
        for i in range(self.solver.num_arcs()):
            flow = int(self.solver.flow(i))
            if flow > 0:
                u = self.index_to_node[self.solver.tail(i)]
                v = self.index_to_node[self.solver.head(i)]
                flow_dict.setdefault(u, {})[v] = flow

        # Combine with direct flows
        if direct_flow_dict:
            for u, flows in direct_flow_dict.items():
                if u not in flow_dict:
                    flow_dict[u] = flows.copy()
                else:
                    flow_dict[u].update(flows)

        return flow_value, flow_dict

    def flow_decomposition(self, flow_dict: Dict[str, Dict[str, int]], source: str, sink: str,
                          requested_flow: Optional[int] = None) -> Tuple[List[Tuple[List[str], List[str], int]],
                                                                       Dict[Tuple[str, str], int]]:
        """Decompose flow into paths."""
        # Use stored flow dictionary to avoid recomputation
        flow_dict = getattr(self, '_flow_dict', flow_dict)
        
        paths, edge_flows = decompose_flow(flow_dict, source, sink, requested_flow)
        
        # Add labels
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

    # BaseGraph interface implementation
    def num_vertices(self) -> int:
        return len(self.node_to_index)
    
    def num_edges(self) -> int:
        return self.solver.num_arcs()
    
    def get_vertices(self) -> Set[str]:
        return set(self.node_to_index.keys())
    
    def get_edges(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        return [(u, v, self.edge_data[(u, v)]) for u, v in self.edges]
    
    def in_degree(self, vertex_id: str) -> int:
        return len(self.incoming_edges[vertex_id])
    
    def out_degree(self, vertex_id: str) -> int:
        return len(self.outgoing_edges[vertex_id])
    
    def degree(self, vertex_id: str) -> int:
        return self.in_degree(vertex_id) + self.out_degree(vertex_id)
    
    def predecessors(self, vertex_id: str) -> Iterator[str]:
        return (u for u, _, _ in self.incoming_edges[vertex_id])
    
    def successors(self, vertex_id: str) -> Iterator[str]:
        return (v for v, _, _ in self.outgoing_edges[vertex_id])
    
    def has_vertex(self, vertex_id: str) -> bool:
        return vertex_id in self.node_to_index

    def has_edge(self, u: str, v: str) -> bool:
        return (u, v) in self.edge_data

    def get_edge_data(self, u: str, v: str) -> Dict:
        return self.edge_data.get((u, v), {})

    def get_vertex(self, vertex_id: str):
        return vertex_id if vertex_id in self.node_to_index else None

    def get_edge_capacity(self, u: str, v: str) -> Optional[int]:
        edge_data = self.edge_data.get((u, v))
        return edge_data['capacity'] if edge_data else None

    def get_node_outflow_capacity(self, source_id: str) -> int:
        """Compute total capacity of outgoing edges from source_id to intermediate nodes."""
        total_capacity = 0
        # Create a set of edges already counted to avoid duplicates
        counted_edges = set()
        
        # Use cached outgoing edges
        for v, capacity, _ in self.outgoing_edges[source_id]:
            if '_' in v and (source_id, v) not in counted_edges:
                total_capacity += capacity
                counted_edges.add((source_id, v))
        
        return total_capacity

    def get_node_inflow_capacity(self, sink_id: str) -> int:
        """Compute total capacity of incoming edges to sink_id from intermediate nodes."""
        total_capacity = 0
        # Create a set of edges already counted to avoid duplicates
        counted_edges = set()
        
        # Use cached incoming edges
        for u, capacity, _ in self.incoming_edges[sink_id]:
            if '_' in u and (u, sink_id) not in counted_edges:
                total_capacity += capacity
                counted_edges.add((u, sink_id))
        
        return total_capacity
    

    def prepare_arbitrage_graph(self, start_node: str, start_token: str, end_token: str) -> Tuple[str, str]:
        """
        Prepare graph for arbitrage analysis with OR-Tools implementation.
        """
        try:
            # Verify start intermediate node exists
            start_intermediate = f"{start_node}_{start_token}"
            if start_intermediate not in self.node_to_index:
                self.logger.warning(f"No intermediate node found for {start_node} with token {start_token}")
                return None, None

            # Store original edges and capacities
            self._temp_edges = []
            source_idx = self.node_to_index[start_node]
            source_arcs = self.arc_adjacency.get(source_idx, [])
            
            for arc_idx, target_idx, capacity in source_arcs:
                target_node = self.index_to_node[target_idx]
                self._temp_edges.append((
                    arc_idx,
                    target_node,
                    self.solver.capacity(arc_idx)
                ))
                # Temporarily set capacity to 0
                self.solver.set_arc_capacity(arc_idx, 0)

            # Restore only the edge to start token intermediate node
            start_inter_idx = self.node_to_index[start_intermediate]
            available_capacity = 0
            for arc_idx, target_idx, _ in source_arcs:
                if target_idx == start_inter_idx:
                    original_capacity = next(
                        cap for a_idx, _, cap in self._temp_edges 
                        if a_idx == arc_idx
                    )
                    self.solver.set_arc_capacity(arc_idx, original_capacity)
                    available_capacity = original_capacity
                    break

            if available_capacity == 0:
                self.logger.warning(f"No edge found from {start_node} to {start_intermediate}")
                self._restore_edges()
                return None, None

            # Create virtual sink
            virtual_sink_id = f"virtual_sink_{start_node}_{start_token}_{end_token}"
            virtual_sink_idx = len(self.node_to_index)
            self.node_to_index[virtual_sink_id] = virtual_sink_idx
            self.index_to_node[virtual_sink_idx] = virtual_sink_id

            # Find end positions using reverse arc adjacency
            edges_added = 0
            source_idx = self.node_to_index[start_node]
            
            # Process incoming edges to start_node directly from reverse_arc_adjacency
            for arc_idx, from_idx, capacity in self.reverse_arc_adjacency.get(source_idx, []):
                from_node = self.index_to_node[from_idx]
                if '_' in from_node:
                    holder, token = from_node.split('_')
                    if token == end_token:
                        # Add edge to virtual sink with limited capacity
                        limited_capacity = min(capacity, available_capacity)
                        arc_idx = self.solver.add_arc_with_capacity(
                            from_idx,
                            virtual_sink_idx,
                            limited_capacity
                        )
                        edges_added += 1

            if edges_added == 0:
                self.logger.warning("No valid end states found for arbitrage")
                self._restore_edges()
                return None, None

            self.logger.debug(f"Added {edges_added} edges to virtual sink")
            return start_node, virtual_sink_id

        except Exception as e:
            self.logger.error(f"Error preparing arbitrage graph: {e}")
            self._restore_edges()
            raise

    def cleanup_arbitrage_graph(self):
        """Clean up temporary changes made for arbitrage analysis."""
        try:
            if hasattr(self, '_temp_edges'):
                # Restore original edge capacities
                for arc_idx, _, capacity in self._temp_edges:
                    self.solver.set_arc_capacity(arc_idx, capacity)
                delattr(self, '_temp_edges')

            # Remove virtual sink from mappings
            virtual_sinks = [
                node_id for node_id in list(self.node_to_index.keys())
                if str(node_id).startswith('virtual_sink_')
            ]
            
            for v_id in virtual_sinks:
                idx = self.node_to_index[v_id]
                del self.node_to_index[v_id]
                del self.index_to_node[idx]

        except Exception as e:
            self.logger.error(f"Error cleaning up arbitrage graph: {e}")
            raise

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
                if self.has_edge(u, start_node):
                    # Add the return flow
                    real_flows[u][start_node] = virtual_flow
        
        return dict(real_flows)

    def _restore_edges(self):
        """Restore temporarily removed edges."""
        try:
            if hasattr(self, '_temp_edges'):
                for arc_idx, _, capacity in self._temp_edges:
                    self.solver.set_arc_capacity(arc_idx, capacity)
                delattr(self, '_temp_edges')
        except Exception as e:
            self.logger.error(f"Error restoring edges: {e}")
            raise