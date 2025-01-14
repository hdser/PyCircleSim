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
    
        groups = [addr for addr in context.agent_manager.address_to_agent.keys() if client.isGroup(addr)]
        if not groups:
            return {}
        group = random.choice(groups)

        addresses = [[addr,group_addr] 
                     for addr in context.agent.accounts.keys() 
                     for group_addr in groups 
                     if (client.isHuman(addr) and client.isTrusted(group_addr,addr))]
        if not addresses:
            return None
        [sender, group] = random.choice(addresses)
            
   
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
        
        addresses = [addr for addr in context.agent.accounts.keys() if client.isHuman(addr)]
        if not addresses:
            return {}
    
        sender = random.choice(addresses)
        
            
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
        
        addresses = [addr for addr in list(context.agent.accounts.keys()) 
                                 if not client.isHuman(addr) and not client.isGroup(addr) and not client.isOrganization(addr)
                                ]
        if not addresses:
            return {}
        
        creator_address = random.choice(addresses)
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
        
        addresses = [addr for addr in list(context.agent.accounts.keys()) 
                                 if (client.isHuman(addr) or client.isGroup(addr)) and (client.balanceOf(addr,client.toTokenId(addr))>96e18)
                                ]
        if not addresses:
            return {}
        
        inviter = random.choice(addresses)
        

        address = next(
            (
                addr for addr in context.agent_manager.address_to_agent.keys()
                if not client.isHuman(addr) and not client.isGroup(addr) and not client.isOrganization(addr) and client.isTrusted(inviter,addr)
            ),
            None  
        )
        if not address:
            return {}
        

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

        
        trusters = [addr for addr in list(context.agent.accounts.keys()) if (client.isHuman(addr) or client.isGroup(addr))]

        if not trusters:
            return {}
        
        truster = random.choice(trusters)

        all_accounts = list(context.agent_manager.address_to_agent.keys())

        trustee = next(
            (
                addr for addr in all_accounts
                if addr != truster and not client.isTrusted(truster, addr)
            ),
            None  
        )
        
        if not trustee:
            return {}

        
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
            

