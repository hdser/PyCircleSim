from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
from .._utils import _analyze_arbitrage
import logging

logger = get_logger(__name__, logging.DEBUG)

@register_implementation("custom_arbPathFinder")
class ArbPathFinder(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Execute pathfinder with unwrapped CRC"""
        sender = context.acting_address.lower()
        
        # Get arbitrage info
        arb_info = context.get_running_state('arb_check')
        if not arb_info:
            return []
            
        client = context.get_client("circleshub")
        if not client:
            return []

        buy_unwrapped = arb_info['buy_unwrapped']
        sell_unwrapped = arb_info['sell_unwrapped']

        cutoff = int(arb_info['received_crc_amount'] / 10**15)
        # Calculate flows
        max_flow, _, edge_flows, _ = _analyze_arbitrage(
            context,
            sender, 
            buy_unwrapped,
            sell_unwrapped,
            cutoff
        )
        print('======== ',max_flow, cutoff)

        if not edge_flows:
            return []

        logger.debug("Original flows:")
        for (f, t), flows in edge_flows.items():
            logger.debug(f"{f} -> {t}: {flows}")

        # Build vertices list first
        vertices = set([sender])  # Start with sender
        node_map = {}  # Map of node IDs to resolved addresses

        # First pass: resolve all addresses and build vertex set
        for (from_node, to_node), token_flows in edge_flows.items():
            if from_node.startswith('virtual_sink_') or to_node.startswith('virtual_sink_'):
                continue

            # Resolve from node
            if from_node not in node_map:
                addr = context.graph_manager.data_ingestion.get_address_for_id(from_node)
                if addr:
                    node_map[from_node] = addr.lower()
                    vertices.add(addr.lower())

            # Resolve to node
            if to_node not in node_map:
                addr = context.graph_manager.data_ingestion.get_address_for_id(to_node)
                if addr:
                    node_map[to_node] = addr.lower()
                    vertices.add(addr.lower())

            # Resolve tokens
            for token_id in token_flows.keys():
                if token_id not in node_map:
                    addr = context.graph_manager.data_ingestion.get_address_for_id(token_id)
                    if addr:
                        node_map[token_id] = addr.lower()
                        vertices.add(addr.lower())

        # Sort vertices and create lookup
        flow_vertices = sorted(list(vertices))
        lookup_map = {addr: idx for idx, addr in enumerate(flow_vertices)}

        logger.debug("Node mappings:")
        for node, addr in node_map.items():
            logger.debug(f"{node} -> {addr}")

        # Build edges and coordinates
        flow_edges = []
        coordinates = []

        # Process edges in order
        for (from_node, to_node), token_flows in edge_flows.items():
            if from_node.startswith('virtual_sink_') or to_node.startswith('virtual_sink_'):
                continue

            if from_node not in node_map or to_node not in node_map:
                continue

            from_addr = node_map[from_node]
            to_addr = node_map[to_node]

            for token_id, flow_value in token_flows.items():
                if token_id not in node_map:
                    continue

                token_addr = node_map[token_id]
                edge_idx = len(flow_edges)

                # Add flow edge
                flow_edges.append({
                    'streamSinkId': 1 if to_addr == sender else 0,
                    'amount': flow_value * 10**15
                })

                # Add coordinates
                coordinates.extend([
                    lookup_map[token_addr],
                    lookup_map[from_addr],
                    lookup_map[to_addr]
                ])

        # Create stream object
        stream = {
            'sourceCoordinate': lookup_map[sender],
            'flowEdgeIds': [i for i, edge in enumerate(flow_edges) if edge['streamSinkId'] == 1],
            'data': bytes()
        }

        # Pack coordinates
        packed_coordinates = bytes([
            b for coord in coordinates
            for b in [(coord >> 8) & 0xff, coord & 0xff]
        ])

        logger.debug("Final parameters:")
        logger.debug(f"Vertices ({len(flow_vertices)}): {flow_vertices}")
        logger.debug(f"Flow edges ({len(flow_edges)}): {flow_edges}")
        logger.debug(f"Stream edge indices: {stream['flowEdgeIds']}")
        logger.debug(f"Coordinate pairs: {[coordinates[i:i+3] for i in range(0, len(coordinates), 3)]}")

        CIRCLES_HUB = '0xc12C1E50ABB450d6205Ea2C3Fa861b3B834d13e8' 
        batch_calls = []
        batch_calls.append(
            ContractCall(
                client_name="circleshub",
                method="setApprovalForAll",
                params={
                    '_operator': CIRCLES_HUB,
                    '_approved': True,
                    'sender': sender,
                    'value': 0
                }
            )
        )

        batch_calls.append(
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
                }
            )
        )

        return batch_calls