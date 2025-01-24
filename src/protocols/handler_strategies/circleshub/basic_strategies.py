from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from ape_ethereum import Ethereum
from eth_pydantic_types import HexBytes
import random


#--------------------------------------------------------------------------------
#-- AUXILIAR FUNCTIONS
#--------------------------------------------------------------------------------

def agent_balances(agent_addr: str, agent_manager, client) -> dict:
    """
    Retrieve the balances of all tokens for a agent.

    Args:
        agent_addr (str): The address of the agent to query balances for.
        agent_manager: The manager object containing agents information.
        client: The client interface to interact with the blockchain.

    Returns:
        dict: A dictionary where keys are token IDs and values are balances.
    """
    all_accounts = agent_manager.address_to_agent.keys()
    
    
    # Create lists for token IDs and accounts using comprehensions
    token_ids = [client.toTokenId(addr) for addr in all_accounts]
    accounts = [agent_addr] * len(all_accounts)

    if not accounts:
        return {}

    # Fetch balances and map them to their respective token IDs
    balances = client.balanceOfBatch(accounts, token_ids)
    return {token_id: balance for token_id, balance in zip(token_ids, balances)}


class BurnStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return {}
        
        client = context.get_client('circleshub')
        if not client:
            return {}
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            

        balances = agent_balances(sender, context.agent_manager, client)
        [tokenid, amount] = next(
            (
                [id, value] for id, value in balances.items() if value >0 
            ),
            [None, None]  
        )
        if not tokenid:
            return {}
        
        
        
        params['_id'] = tokenid  # type: uint256
        params['_amount'] = amount  # type: uint256
        params['_data'] = b""   # type: bytes
        
        return params


class CalculateIssuanceWithCheckStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_human'] = None  # type: address
        
        
        

        return params



class GroupMintStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return None

        groups = context.get_filtered_addresses(
            client.isGroup,
            cache_key='groups_list'
        )
        if not groups:
            return {}
        group = random.choice(groups)

        valid_senders = context.get_or_cache(
            f'valid_senders_for_{group}',
            lambda: [
                addr for addr in context.agent.accounts.keys()
                if client.isHuman(addr) and client.isTrusted(group, addr)
            ]
        )
        if not valid_senders:
            return None
        
        sender = random.choice(valid_senders)
        collateral_avatar = sender
            
        

        collateral_id = client.toTokenId(collateral_avatar)
        balance = client.balanceOf(collateral_avatar, collateral_id)
        if balance == 0:
            return {}

        amount = int(balance * random.uniform(0.1, 0.3))
        if amount == 0:
            return {}
        
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        params['_group'] = group  # type: address
        params['_collateralAvatars'] = [collateral_avatar]  # type: address[]
        params['_amounts'] = [amount]  # type: uint256[]
        params['_data'] = b""   # type: bytes
        
        return params


class MigrateStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_owner'] = None  # type: address
        
        
        
        
        
        params['_avatars'] = None  # type: address[]
        
        
        
        
        
        params['_amounts'] = None  # type: uint256[]
        
        
        

        return params




class OperateFlowMatrixStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        client = context.get_client('circleshub')
        if not client:
            return None

        addresses = [addr for addr in list(context.agent_manager.address_to_agent.keys()) if addr != sender]
        if not addresses:
            return {}
        receiver = random.choice(addresses)

        # Get flow analysis results
        constraints = context.agent.profile.action_configs['circleshub_OperateFlowMatrix'].constraints
        if 'max_flow' in constraints:
            max_flow = min(constraints['max_flow'],1e9)
        if 'min_flow' in constraints:
            min_flow = max(constraints['min_flow'],0)
        
        cutoff = str(random.randint(min_flow * 1e3, max_flow * 1e3)) # mCRC
        #cutoff = str(1000000)
        _, _, simplified_edge_flows, _ = self._analyze_flow(context, sender, receiver, cutoff)
        
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


        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            

        params['_flowVertices'] = flow_vertices  # type: address[]
        params['_flow'] = flow_edges
        params['_streams'] = [stream]
        params['_packedCoordinates'] = packed_coordinates  # type: bytes
        
        return params


class PersonalMintStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return {}
        
        valid_senders = context.get_filtered_addresses(
            lambda addr: client.isHuman(addr),
            cache_key=f'human_addresses'
        )
        if not valid_senders:
            return {}
    
        sender = random.choice(valid_senders)
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        

        return params


class RegisterCustomGroupStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_mint'] = None  # type: address
        
        
        
        
        
        params['_treasury'] = None  # type: address
        
        
        
        
        
        params['_name'] = None  # type: string
        
        
        
        
        
        params['_symbol'] = None  # type: string
        
        
        
        
        
        params['_metadataDigest'] = None  # type: bytes32
        
        
        

        return params



class RegisterGroupStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return {}
        
        unregistered = context.get_filtered_addresses(
            lambda addr: not (client.isHuman(addr) or client.isGroup(addr) or client.isOrganization(addr)),
            cache_key=f'unregistered_addresses_{context.agent.agent_id}'
        )
        if not unregistered:
            return {}
        
        creator_address = random.choice(unregistered)
        group_number = getattr(context.agent, 'group_count', 0) + 1
        mint_policy = "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60"

            
        # Initialize parameters with transaction details
        params = {
            'sender': creator_address,     # Transaction sender
            'value': 0            # Transaction value
        }
 
        params['_mint'] = mint_policy  # type: address
        params['_name'] = f"RingsGroup{creator_address[:4]}{group_number}"  # type: string
        params['_symbol'] = f"RG{creator_address[:2]}{group_number}"  # type: string
        params['_metadataDigest'] = HexBytes("0x00")   # type: bytes32

        return params



class RegisterHumanStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return None
        
        inviters = context.get_filtered_addresses(
            lambda addr: (client.isHuman(addr) or client.isGroup(addr)) and 
                        (client.balanceOf(addr, client.toTokenId(addr)) > 96e18),
            cache_key=f'potential_inviters'
        )
        if not inviters:
            return {}
        
        inviter = random.choice(inviters)
        

        unregistered_trusted = context.get_or_cache(
            f'unregistered_trusted_{inviter}',
            lambda: [
                addr for addr in context.agent_manager.address_to_agent.keys()
                if not client.isHuman(addr) and 
                not client.isGroup(addr) and 
                not client.isOrganization(addr) and 
                client.isTrusted(inviter, addr)
            ]
        )
        
        if not unregistered_trusted:
            return {}
        
        address = random.choice(unregistered_trusted)
        
            
        # Initialize parameters with transaction details
        params = {
            'sender': address,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        params['_inviter'] = inviter  # type: address
        params['_metadataDigest'] = HexBytes("0x00")  # type: bytes32

        return params


class RegisterOrganizationStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_name'] = None  # type: string
        
        
        
        
        
        params['_metadataDigest'] = None  # type: bytes32
        
        
        

        return params


class SafeBatchTransferFromStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_from'] = None  # type: address
        
        
        
        
        
        params['_to'] = None  # type: address
        
        
        
        
        
        params['_ids'] = None  # type: uint256[]
        
        
        
        
        
        params['_values'] = None  # type: uint256[]
        
        
        
        
        
        params['_data'] = None  # type: bytes
        
        
        

        return params



class SafeTransferFromStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return {}
        
        senders = [[addr, client.toTokenId(addr), client.balanceOf(addr, client.toTokenId(addr))] for addr in context.agent.accounts.keys() 
                  if client.balanceOf(addr, client.toTokenId(addr))>0]
        if not senders:
            return {}
        [sender, tokenid, balance] = random.choice(senders)
        
        addresses = list(context.agent_manager.address_to_agent.keys())
        if not addresses:
            return {}
        receiver = random.choice(addresses)

        if balance == 0:
            return {}

        amount = int(balance * random.uniform(0.1, 0.3))
        if amount == 0:
            return {}


        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }

        params['_from'] = sender  # type: address
        params['_to'] = receiver  # type: address
        params['_id'] = tokenid  # type: uint256
        params['_value'] = amount  # type: uint256
        params['_data'] = b""  # type: bytes
        
        return params


class SetAdvancedUsageFlagStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_flag'] = None  # type: bytes32
        
        
        

        return params


class SetApprovalForAllStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['_operator'] = None  # type: address
        
        
        
        
        
        params['_approved'] = None  # type: bool
        
        
        

        return params


class StopStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        

        return params



class TrustStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        # Parameters
        block_timestamp = context.chain.blocks.head.timestamp
        expiry_delta = 365 * 24 * 60 * 60
        expiry = int(block_timestamp + expiry_delta)

        client = context.get_client('circleshub')
        if not client:
            return None

        
        trusters = context.get_filtered_addresses(
            lambda addr: client.isHuman(addr) or client.isGroup(addr),
            cache_key=f'potential_trusters'
        )
        if not trusters:
            return {}
        
        truster = random.choice(trusters)

        potential_trustees = context.get_or_cache(
            f'potential_trustees_{truster}',
            lambda: [
                addr for addr in context.agent_manager.address_to_agent.keys()
                if addr != truster and not client.isTrusted(truster, addr)
            ]
        )
        
        if not potential_trustees:
            return {}
        
        trustee = random.choice(potential_trustees)

            
        # Initialize parameters with transaction details
        params = {
            'sender': truster,     # Transaction sender
            'value': 0            # Transaction value
        }

        params['_trustReceiver'] = trustee  # type: address
        params['_expiry'] = expiry  # type: uint96

        return params


            
class WrapStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None

        # Get the specific client we need
        client = context.get_client('circleshub')
        if not client:
            return None

       # inflation_day_zero = context.get_contract_state('CirclesHub', 'inflationDayZero')
       # avatars_list = context.get_contract_state('CirclesHub', 'avatars', [])

        id = client.toTokenId(sender) 
        balance = client.balanceOf(sender, id)
        if balance == 0:
            return {}
            

        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }

        params['_avatar'] = sender  # type: address
        params['_amount'] = int(balance/10.0)  # type: uint256
        params['_type'] = 0  # type: uint8

        return params




class MulticallPathfinderTransferStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return None
        
        sender = self.get_sender(context)
        if not sender:
            return None
        
        addresses = [addr for addr in list(context.agent_manager.address_to_agent.keys()) if addr != sender]
        if not addresses:
            return {}
        receiver = random.choice(addresses)

        multicall_data = {
            "tx_params": {"sender": sender, "value": 0}
        }

        cutoff = str(10000)
        _, _, simplified_edge_flows, _ = self._analyze_flow(context, sender, receiver, cutoff)
        
        i=0
        for edge, token_flow in simplified_edge_flows.items():
                from_addr = context.graph_manager.data_ingestion.get_address_for_id(edge[0])
                to_addr = context.graph_manager.data_ingestion.get_address_for_id(edge[1])
                token_graph_id, token_flow_redux = list(token_flow.items())[0]
                token_addr = context.graph_manager.data_ingestion.get_address_for_id(token_graph_id)
                token_id = client.toTokenId(token_addr)
                token_flow = int(token_flow_redux * 1e15)
            
                multicall_data[f'circleshub_safeTransferFrom_{i}'] = {
                    '_from': from_addr,
                    '_to': to_addr,
                    '_id': token_id,
                    '_value': token_flow,
                    '_data': b"",
                }
                i+=1

        if 'circleshub_safeTransferFrom_0' not in multicall_data.keys():
            return {}
        
        return multicall_data



class MulticallCase1Strategy(BaseStrategy):
    """
    Example strategy that returns a dict of subcalls:
    { "circleshub_RegisterCustomGroup": {...}, "circleshub_Trust": {...}, ... }

    Each key is an 'action_name' like "circleshub_SomeFunction".
    Each value is the normal parameter dict you would pass for that action.
    """

    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('circleshub')
        if not client:
            return None
        
        sender = self.get_sender(context)
        if not sender:
            return None


        # subcall #1: "circleshub_setApprovalForAll"

        subcall1_params = {
            '_operator': "0xD608978aD1e1473fa98BaD368e767C5b11e3b3cE",
            '_approved': True
        }

        # subcall #2: "circleshub_safeTransferFrom"
        token_id = client.toTokenId("0x42cEDde51198D1773590311E2A340DC06B24cB37")
        subcall2_params = {
            '_from': "0x42cEDde51198D1773590311E2A340DC06B24cB37",  
            '_to': "0xD608978aD1e1473fa98BaD368e767C5b11e3b3cE",
            '_id': token_id,
            '_value': 48000000000000000000,
            '_data': b'0x0000000000000000000000006a023ccd1ff6f2045c3309768ead9e68f978f6e1'
        }
        
        # Return them under their respective action-names
        return {
            "tx_params": {"sender": '0x42cEDde51198D1773590311E2A340DC06B24cB37', "value": 0},
            "circleshub_setApprovalForAll": subcall1_params,
            "circleshub_safeTransferFrom": subcall2_params,
        }
