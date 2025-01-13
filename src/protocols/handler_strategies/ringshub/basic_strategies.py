from typing import Dict, Any, Optional
import random
from eth_pydantic_types import HexBytes
from ape_ethereum import Ethereum
from src.framework.core import SimulationContext
from src.protocols.handler_strategies.base import BaseStrategy


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



#--------------------------------------------------------------------------------

class BurnStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)

        if not sender:
            return {}
        
        client = context.get_client('ringshub')
        if not client:
            return None

        balances = agent_balances(sender, context.agent_manager, client)
        #for ids, _ in balances.iterrows():
        #    addr = Ethereum.decode_address(ids)
        #    if client.isTrusted()
        tokenid = None
        amount = None
        for id, value in balances.items():
            if value > 0:
                amount = value
                tokenid = id
            
        return {
            'sender': sender,
            'value': 0
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

        sender = self.get_sender(context)
        if not sender:
            return {}


        client = context.get_client('ringshub')
        if not client:
            return None

        groups = []
        all_accounts = context.agent_manager.address_to_agent.keys()
        for addr in all_accounts:
            if client.isGroup(addr) and addr != sender:
                groups.append(addr)

        if not groups:
            return {}
            

        group = random.choice(groups)
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
        client = context.get_client('ringshub')
        if not client:
            return None
        
        mintable_accounts = []
        for address in context.agent.accounts.keys():
            if client.isHuman(address) and not client.stopped(address):
                issuance, start_period, _ = client.calculateIssuance(address)
                if issuance != 0 and context.chain.blocks.head.timestamp >= start_period:
                    mintable_accounts.append(address)
        
        if not mintable_accounts:
            return {}
            
        return {
            'sender': random.choice(mintable_accounts)
        }


class RegisterCustomGroupStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        client = context.get_client('ringshub')
        if not client:
            return None
        
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
        client = context.get_client('ringshub')
        if not client:
            return None
        
        addresses = []
        for addr in context.agent.accounts.keys():
            if not client.isGroup(addr) and not client.isHuman(addr) and not client.isOrganization(addr):
                addresses.append(addr)

        if addresses:
            creator_address = random.choice(addresses)
        else:
            if len(context.agent.accounts) <= context.agent.profile.target_account_count:
                creator_address, _ = context.agent.create_account()
                context.agent_manager.address_to_agent[creator_address] = context.agent.agent_id
            else:
                return {}

        group_number = getattr(context.agent, 'group_count', 0) + 1
        return {
            'sender': creator_address,
            '_name': f"RingsGroup{creator_address[:4]}{group_number}",
            '_symbol': f"RG{creator_address[:2]}{group_number}",
            '_mint': "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60",
            '_metadataDigest': HexBytes("0x00")
        }
    


class RegisterHumanStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:

        client = context.get_client('ringshub')
        if not client:
            return None
        
        addresses = []
        for addr in context.agent.accounts.keys():
            if not client.isGroup(addr) and not client.isHuman(addr) and not client.isOrganization(addr):
                addresses.append(addr)

        if addresses:
            address = random.choice(addresses)
        else:
            if len(context.agent.accounts) <= context.agent.profile.target_account_count:
                address, _ = context.agent.create_account()
                context.agent_manager.address_to_agent[address] = context.agent.agent_id
            else:
                return {}

        return {
            "sender": address,
            "_inviter": "0x0000000000000000000000000000000000000000",
            "_metadataDigest": HexBytes("0x00")
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
        trusted_addresses = context.agent.state.get('trusted_addresses', set())
        if not trusted_addresses:
            return {}

        sender = self.get_sender(context)
        if not sender:
            return {}
        
        rings_client = context.get_client('ringshub')
        if not rings_client:
            return None

        receiver = random.choice(list(trusted_addresses))
        id = rings_client.toTokenId(sender)
        balance = rings_client.balanceOf(sender, id)

        if balance == 0:
            return {}

        amount = int(balance * random.uniform(0.1, 0.3))
        if amount == 0:
            return {}

        return {
            'sender': sender,
            '_from': sender,
            '_to': receiver,
            '_id': id,
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

        truster = self.get_sender(context)

        rings_client = context.get_client('ringshub')
        if not rings_client:
            return None

        all_accounts = context.agent_manager.address_to_agent.keys()
        potential_trustees = []
        for addr in all_accounts:
            if (rings_client.isHuman(addr) or rings_client.isGroup(addr)) and addr != truster and not rings_client.isTrusted(truster,addr):
                potential_trustees.append(addr)
        
        if not potential_trustees:
            return {}

        trustee = random.choice(potential_trustees)
        expiry = int(block_timestamp + expiry_delta)

        return {
            'sender': truster,
            '_trustReceiver': trustee,
            '_expiry': expiry,
        }


class WrapStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return {}
            
        rings_client = context.get_client('ringshub')
        if not rings_client:
            return None
        
        id = rings_client.toTokenId(sender) 
        balance = rings_client.balanceOf(sender, id)
        if balance == 0:
            return {}
            
        return {
            "sender": sender,
            "_avatar": sender,
            "_amount": int(balance/10.0),
            "_type": 0
        }

