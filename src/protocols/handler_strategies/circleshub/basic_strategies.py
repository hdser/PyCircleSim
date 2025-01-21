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

        balances = agent_balances(sender, context.agent_manager, client)


        [tokenid, amount] = next(
            (
                [id, value] for id, value in balances.items() if value >0 
            ),
            [None, None]  
        )
        if not tokenid:
            return {}
            
        return {
            'sender': sender
            ,'_id': tokenid
            ,'_amount': amount
            ,'_data':  b"" 
        }


class CalculateIssuanceWithCheckStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_human': None
            
        }


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
        
        return {
            'sender': sender,
            '_group': group,
            '_collateralAvatars': [collateral_avatar],  
            '_amounts': [amount],  
            '_data': b"" 
        }


class MigrateStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_owner': None
            
            ,'_avatars': None
            
            ,'_amounts': None
            
        }


class OperateFlowMatrixStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_flowVertices': None
            
            ,'_flow': None
            
            ,'_streams': None
            
            ,'_packedCoordinates': None
            
        }



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
        
            
        return {
            'sender': sender
        }


class RegisterCustomGroupStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_mint': None
            
            ,'_treasury': None
            
            ,'_name': None
            
            ,'_symbol': None
            
            ,'_metadataDigest': None
            
        }

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

        return {
            'sender': creator_address
            ,'_mint': mint_policy
            ,'_name': f"RingsGroup{creator_address[:4]}{group_number}"
            ,'_symbol': f"RG{creator_address[:2]}{group_number}"
            ,'_metadataDigest': HexBytes("0x00")   
        }


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
        

        return {
            'sender': address
            ,'_inviter': inviter
            ,'_metadataDigest': HexBytes("0x00")
        }


class RegisterOrganizationStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_name': None
            
            ,'_metadataDigest': None
            
        }


class SafeBatchTransferFromStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_from': None
            
            ,'_to': None
            
            ,'_ids': None
            
            ,'_values': None
            
            ,'_data': None
            
        }


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

        sender = '0x42cEDde51198D1773590311E2A340DC06B24cB37'
        receiver = '0x14c16ce62d26fd51582a646e2e30a3267b1e6d7e'
        tokenid = 499950623275108955190615340282081639491279259873
        amount = 10000000000000000000
        return {
            'sender': sender,
            '_from': sender,
            '_to': receiver,
            '_id': tokenid,
            '_value': amount,
            '_data': b"",
        }


class SetAdvancedUsageFlagStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_flag': None
            
        }


class SetApprovalForAllStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_operator': None
            
            ,'_approved': None
            
        }


class StopStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
        }


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

        
        return {
            'sender': truster,
            '_trustReceiver': trustee,
            '_expiry': expiry,
        }


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
            
        return {
            "sender": sender,
            "_avatar": sender,
            "_amount": int(balance/10.0),
            "_type": 0
        }
            

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
                print(edge,token_flow)
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
        
        print('==-=-=-',multicall_data)
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
        # Example subcall #1: "circleshub_RegisterCustomGroup"
        subcall1_params = {
            '_mint': "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60",  
            '_name': f"Group_{random.randint(1000,9999)}",
            '_symbol': f"GRP_{random.randint(1000,9999)}",
            '_metadataDigest': b"\x00"
        }
        
        # Example subcall #2: "circleshub_Trust"
        # For a trust subcall, you might pick a random trustee:
        trustee = sender  # trivial example, obviously normally a different address
        expiry = context.chain.blocks.head.timestamp + 365*24*60*60

        truster = sender
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

        subcall2_params = {
            '_trustReceiver': trustee,
            '_expiry': expiry
        }

        trustee = random.choice(potential_trustees)
        subcall3_params = {
            '_trustReceiver': trustee,
            '_expiry': expiry
        }

        # Return them under their respective action-names
        return {
            "tx_params": {"sender": sender, "value": 0},
            "circleshub_registerGroup": subcall1_params,
            "circleshub_trust": subcall2_params,
            # Optionally add more subcalls
        }
