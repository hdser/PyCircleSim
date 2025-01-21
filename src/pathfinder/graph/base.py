from abc import abstractmethod
from typing import Set, Dict, Any, Optional, Iterator, List, Tuple, Callable

class BaseGraph:
    """Abstract base class defining the interface for all graph implementations."""
    
    @abstractmethod
    def num_vertices(self) -> int:
        """Return the total number of vertices in the graph."""
        pass
    
    @abstractmethod
    def num_edges(self) -> int:
        """Return the total number of edges in the graph."""
        pass
    
    @abstractmethod
    def has_vertex(self, vertex_id: str) -> bool:
        """Check if a vertex exists in the graph."""
        pass

    @abstractmethod
    def has_edge(self, u: str, v: str) -> bool:
        """Check if an edge exists between two vertices."""
        pass

    @abstractmethod
    def get_edge_data(self, u: str, v: str) -> Dict[str, Any]:
        """Get edge attributes."""
        pass
    
    @abstractmethod
    def get_vertices(self) -> Set[str]:
        """Return set of all vertex IDs."""
        pass
    
    @abstractmethod
    def get_edges(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Return list of all edges with their data."""
        pass
    
    @abstractmethod
    def in_degree(self, vertex_id: str) -> int:
        """Return number of incoming edges for a vertex."""
        pass
    
    @abstractmethod
    def out_degree(self, vertex_id: str) -> int:
        """Return number of outgoing edges for a vertex."""
        pass
    
    @abstractmethod
    def degree(self, vertex_id: str) -> int:
        """Return total degree (in + out) for a vertex."""
        pass
    
    @abstractmethod
    def predecessors(self, vertex_id: str) -> Iterator[str]:
        """Return iterator over predecessor vertices."""
        pass
    
    @abstractmethod
    def successors(self, vertex_id: str) -> Iterator[str]:
        """Return iterator over successor vertices."""
        pass
    
    @abstractmethod
    def get_edge_capacity(self, u: str, v: str) -> Optional[int]:
        """Get capacity of edge between u and v."""
        pass

    @abstractmethod
    def get_node_outflow_capacity(self, source_id: str) -> int:
        """Compute total capacity of outgoing edges from source_id to nodes with '_' in their IDs."""
        pass

    @abstractmethod
    def get_node_inflow_capacity(self, sink_id: str) -> int:
        """Compute total capacity of incoming edges to sink_id from nodes with '_' in their IDs."""
        pass

    @abstractmethod
    def compute_flow(self, source: str, sink: str, flow_func: Optional[Callable] = None,
                    requested_flow: Optional[str] = None) -> Tuple[int, Dict[str, Dict[str, int]]]:
        """Compute flow between source and sink nodes."""
        pass

    @abstractmethod
    def flow_decomposition(self, flow_dict: Dict[str, Dict[str, int]], source: str, sink: str,
                          requested_flow: Optional[int] = None) -> Tuple[List[Tuple[List[str], List[str], int]], 
                                                                       Dict[Tuple[str, str], int]]:
        """Decompose flow into paths."""
        pass

    @abstractmethod
    def simplified_flow_decomposition(self, original_paths: List[Tuple[List[str], List[str], int]]) -> List[Tuple[List[str], List[str], int]]:
        """Create simplified paths."""
        pass

    @abstractmethod
    def prepare_arbitrage_graph(self, start_node: str, start_token: str, end_token: str) -> Tuple[str, str]:
        """
        Prepare graph for arbitrage max-flow computation by adding virtual sink.
        
        Args:
            start_node: Node to start from
            start_token: Token to start with 
            end_token: Token to end with
            
        Returns:
            Tuple of (start_id, virtual_sink_id) to use for max flow computation
        """
        pass
        
    @abstractmethod
    def cleanup_arbitrage_graph(self):
        """Remove any temporary nodes/edges added for arbitrage computation."""
        pass
        
    @abstractmethod
    def interpret_arbitrage_flow(self, flow_dict: Dict[str, Dict[str, int]], 
                               start_node: str, virtual_sink: str) -> Dict[str, Dict[str, int]]:
        """Convert arbitrage flow dict into actual token flows."""
        pass

class GraphCreator:
    @staticmethod
    def create_graph(graph_type: str, edges: List[Tuple[str, str]], capacities: List[float], 
                    tokens: List[str]) -> BaseGraph:
        """Factory method to create appropriate graph implementation."""
        if graph_type == 'networkx':
            from .networkx_graph import NetworkXGraph
            return NetworkXGraph(edges, capacities, tokens)
        elif graph_type == 'ortools':
            from .ortools_graph import ORToolsGraph
            return ORToolsGraph(edges, capacities, tokens)
        else:
            raise ValueError(f"Unsupported graph type: {graph_type}")