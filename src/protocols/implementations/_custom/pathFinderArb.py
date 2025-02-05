from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging
from ._utils import _analyze_arbitrage
import random

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_pathFinderArb")
class PathFinderArb(BaseImplementation):

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        sender = context.acting_address


        constraints = context.agent.profile.get_action_config("custom_setupLBP").constraints
        START_TOKEN = constraints.get('START_TOKEN',sender)
        END_TOKEN = constraints.get('END_TOKEN','0xA6247834B41771022498F63CAE8820fFEE208265')

        _, _, simplified_edge_flows, _ = _analyze_arbitrage(context, sender, START_TOKEN, END_TOKEN)

        
        filtered_edge_flows = {}
        for edge, token_flows in simplified_edge_flows.items():
            # Skip any edge where either endpoint is a virtual sink.
            if edge[0].startswith("virtual_sink_") or edge[1].startswith("virtual_sink_"):
                continue
            filtered_edge_flows[edge] = token_flows

        def resolve_node(node_id: str) -> str:
            """
            If node_id is composite (e.g. "24_543"), use only the first part.
            Otherwise, use the mapping from GraphLoader.
            """
            if '_' in node_id:
                pure_id = node_id.split('_')[0]
                resolved = context.graph_manager.data_ingestion.get_address_for_id(pure_id)
                return resolved if resolved is not None else node_id
            else:
                return context.graph_manager.data_ingestion.get_address_for_id(node_id)

        # Build the set of addresses that will be vertices in call.
        address_set = set()
        # Always include the sender.
        address_set.add(sender.lower())
        for edge, token_flows in filtered_edge_flows.items():
            from_addr = resolve_node(edge[0])
            to_addr = resolve_node(edge[1])
            if from_addr:
                address_set.add(from_addr.lower())
            if to_addr:
                address_set.add(to_addr.lower())
            for token_id in token_flows.keys():
                token_addr = context.graph_manager.data_ingestion.get_address_for_id(token_id)
                if token_addr:
                    address_set.add(token_addr.lower())

        flow_vertices = sorted(list(address_set))
        lookup_map = {addr: idx for idx, addr in enumerate(flow_vertices)}

        # Build the flow edges and the coordinate array.
        flow_edges = []
        coordinates = []
        for edge, token_flows in filtered_edge_flows.items():
            from_addr = resolve_node(edge[0])
            to_addr = resolve_node(edge[1])
            for token_id, flow_value in token_flows.items():
                token_addr = context.graph_manager.data_ingestion.get_address_for_id(token_id)
                amount = int(flow_value * 1e15)
                flow_edges.append({
                    'streamSinkId': 1 if to_addr.lower() == sender.lower() else 0,
                    'amount': amount
                })
                coordinates.extend([
                    lookup_map[token_addr.lower()],
                    lookup_map[from_addr.lower()],
                    lookup_map[to_addr.lower()]
                ])

        packed_coordinates = bytes([
            b for coord in coordinates
            for b in [(coord >> 8) & 0xff, coord & 0xff]
        ])

        stream = {
            'sourceCoordinate': lookup_map[sender.lower()],
            'flowEdgeIds': [i for i, edge in enumerate(flow_edges) if edge['streamSinkId'] == 1],
            'data': bytes()
        }

        return [
            ContractCall(
                client_name="circleshub",
                method="operateFlowMatrix",
                params={
                    "sender": sender,
                    "value": 0,
                    "_flowVertices": flow_vertices,
                    "_flow": flow_edges,
                    "_streams": [stream],
                    "_packedCoordinates": packed_coordinates,
                },
            )
        ]
