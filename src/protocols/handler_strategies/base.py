from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List, Callable
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
import random
import logging 

logger = get_logger(__name__, logging.DEBUG)

class BaseStrategy(ABC):
    """Base class for all parameter generation strategies"""
    
    def __init__(self):
        """Initialize strategy"""
        pass

    @abstractmethod
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        """Get parameters for an action"""
        pass

    def get_constraints(self,context: SimulationContext, name, step_name: Optional[str] = None):
        constraints = {}

        if 'sequences' in context.agent.profile:
            for sequence in context.agent.profile.sequences:
                if sequence.name==name:
                    for step in sequence.steps:
                        if step.batchcall:
                            if step_name in step.batchcall.keys():
                                constraints = step.constraints
                        else:
                            constraints = step.constraints

        else:
            constraints = context.agent.profile.action_configs[name].constraints
        return constraints

    def get_sender(self, context: SimulationContext) -> Optional[str]:
        """Helper to get the appropriate sender address"""
        if not context.agent.accounts:
            return None


        # If no profile or no sequences defined, use random account
        if not hasattr(context.agent, 'profile') or not hasattr(context.agent.profile, 'sequences'):
            return random.choice(list(context.agent.accounts.keys()))

        # If there are no sequences or empty sequences list, use random account    
        if not context.agent.profile.sequences:
            return random.choice(list(context.agent.accounts.keys()))

        # Check for active sequence
        for sequence in context.agent.profile.sequences:
            # Skip if sequence states not initialized
            if not hasattr(context.agent, 'sequence_states'):
                continue
                
            # Check each address's state for this sequence
            for addr, states in context.agent.sequence_states.items():
                if not states:  # Skip if no states for this address
                    continue
                    
                seq_state = states.get(sequence.name)
                if not seq_state:  # Skip if no state for this sequence
                    continue
                    
                # Check if sequence is active and not completed
                if (seq_state.get("active", True) and
                    seq_state.get("current_step_index", 0) < len(sequence.steps) and
                    seq_state.get("sequence_executions", 0) < sequence.max_executions):
                    return addr

        # Default to random account if no active sequence found
        return random.choice(list(context.agent.accounts.keys()))
    
    def _analyze_flow(self, context: SimulationContext, source: str, sink: str, cutoff: str = None) -> Tuple[int, list, Dict, Dict]:
        """Analyze flow between addresses"""
        try:
            if not context.graph_manager:
                logger.warning("No graph manager available - rebuilding")
                context.rebuild_graph()
                
                if not context.graph_manager:
                    logger.error("Failed to create graph manager")
                    return 0, [], {}, {}

            # Debug graph state
            logger.debug(f"Analyzing flow from {source} to {sink}")
            logger.debug(f"Graph has {context.graph_manager.graph.num_vertices()} vertices and "
                        f"{context.graph_manager.graph.num_edges()} edges")

            
            source_id = context.graph_manager.data_ingestion.get_id_for_address(source)
            sink_id = context.graph_manager.data_ingestion.get_id_for_address(sink)
            # Verify source and sink exist in graph
            if not context.graph_manager.graph.has_vertex(source_id):
                logger.warning(f"Source {source} not in graph")
                return 0, [], {}, {}
            if not context.graph_manager.graph.has_vertex(sink_id):
                logger.warning(f"Sink {sink} not in graph")
                return 0, [], {}, {}

            return context.graph_manager.analyze_flow(
                source=source,
                sink=sink,
                cutoff=cutoff
            )

        except Exception as e:
            logger.error(f"Flow analysis failed: {e}", exc_info=True)
            return 0, [], {}, {}
        