from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
from ape_ethereum.ecosystem import encode
from ._utils import _analyze_flow
import random


@register_implementation("custom_pathFinderTransfer")
class PathFinderTransfer(BaseImplementation):

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleshub_operateFlowMatrix"
        ).constraints

        addresses = [addr for addr in list(context.agent.accounts.keys()) if addr != sender]
        if not addresses:
            return {}
        
        receiver = random.choice(addresses)

        # Get flow analysis results
        max_flow = constraints.get('max_flow',1e9)
        min_flow = constraints.get('min_flow',0)
        cutoff = str(random.randint(min_flow * 1e3, max_flow * 1e3)) # mCRC

        _, _, simplified_edge_flows, _ = _analyze_flow(context, sender, receiver, cutoff)
        
        # Transform addresses to sorted unique list for flow vertices
        address_set = set()
        address_set.add(sender.lower())
        address_set.add(receiver.lower())
        
        # Add all addresses from edges and tokens
        for edge, token_flows in simplified_edge_flows.items():
            from_addr = context.graph_manager.data_ingestion.get_address_for_id(edge[0])
            to_addr = context.graph_manager.data_ingestion.get_address_for_id(edge[1])
            
            address_set.add(from_addr.lower())
            address_set.add(to_addr.lower())
            
            # Add addresses for all token owners in this edge
            for token_id in token_flows.keys():
                token_addr = context.graph_manager.data_ingestion.get_address_for_id(token_id)
                address_set.add(token_addr.lower())

        # Sort addresses
        flow_vertices = sorted(list(address_set))
        
        # Create lookup map
        lookup_map = {addr: idx for idx, addr in enumerate(flow_vertices)}

        # Create flow edges and coordinates
        flow_edges = []
        coordinates = []
        
        for edge, token_flows in simplified_edge_flows.items():
            from_addr = context.graph_manager.data_ingestion.get_address_for_id(edge[0])
            to_addr = context.graph_manager.data_ingestion.get_address_for_id(edge[1])
            
            # Handle all token flows for this edge
            for token_id, flow_value in token_flows.items():
                token_addr = context.graph_manager.data_ingestion.get_address_for_id(token_id)
                
                # Convert flow to proper units
                amount = int(flow_value * 1e15)
                
                # Add flow edge
                flow_edges.append({
                    'streamSinkId': 1 if to_addr.lower() == receiver.lower() else 0,
                    'amount': amount
                })
                
                # Add coordinates for (tokenOwner, sender, receiver)
                coordinates.extend([
                    lookup_map[token_addr.lower()],
                    lookup_map[from_addr.lower()],
                    lookup_map[to_addr.lower()]
                ])

        # Pack coordinates into bytes
        packed_coordinates = bytes([
            b for coord in coordinates
            for b in [(coord >> 8) & 0xff, coord & 0xff]
        ])

        # Create stream object
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
