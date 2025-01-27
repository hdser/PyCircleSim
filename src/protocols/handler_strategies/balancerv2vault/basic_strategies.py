from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core.context import SimulationContext
import random
from ape_ethereum.ecosystem import encode
from ape import Contract
import logging
from src.framework.logging import get_logger

logger = get_logger(__name__, logging.DEBUG)


class BatchSwapStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['kind'] = None  # type: uint8
        
        
        
        
        # Initialize swaps tuple fields
        swaps_fields = {
            
            'poolId': None,  # bytes32
            
            'assetInIndex': None,  # uint256
            
            'assetOutIndex': None,  # uint256
            
            'amount': None,  # uint256
            
            'userData': None,  # bytes
            
        }
        params['swaps'] = swaps_fields
        
        
        
        
        params['assets'] = None  # type: address[]
        
        
        
        
        # Initialize funds tuple fields
        funds_fields = {
            
            'sender': None,  # address
            
            'fromInternalBalance': None,  # bool
            
            'recipient': None,  # address
            
            'toInternalBalance': None,  # bool
            
        }
        params['funds'] = funds_fields
        
        
        
        
        params['limits'] = None  # type: int256[]
        
        
        
        
        
        params['deadline'] = None  # type: uint256
        
        
        

        return params


class DeregisterTokensStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['poolId'] = None  # type: bytes32
        
        
        
        
        
        params['tokens'] = None  # type: address[]
        
        
        

        return params


class ExitPoolStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['poolId'] = None  # type: bytes32
        
        
        
        
        
        params['sender_account'] = None  # type: address (renamed from 'sender')
        
        
        
        
        
        params['recipient'] = None  # type: address
        
        
        
        
        # Initialize request tuple fields
        request_fields = {
            
            'assets': None,  # address[]
            
            'minAmountsOut': None,  # uint256[]
            
            'userData': None,  # bytes
            
            'toInternalBalance': None,  # bool
            
        }
        params['request'] = request_fields
        
        

        return params


class FlashLoanStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['recipient'] = None  # type: address
        
        
        
        
        
        params['tokens'] = None  # type: address[]
        
        
        
        
        
        params['amounts'] = None  # type: uint256[]
        
        
        
        
        
        params['userData'] = None  # type: bytes
        
        
        

        return params


class JoinPoolStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return {}
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,    
            'value': 0           
        }

        if not isinstance(context.network_state['contract_states'].get('BalancerV2LBPFactory'), dict):
            return {}
        
        if not isinstance(context.network_state['contract_states']['BalancerV2LBPFactory'].get('state'), dict):
            return {}
        
        if not isinstance(context.network_state['contract_states']['BalancerV2LBPFactory']['state'].get('LBPs'), dict):
            return {}
        
        LBPs_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']['LBPs']
        poolId = random.choice(list(LBPs_state.keys()))
        assets = LBPs_state[poolId]['tokens']
        vault_address = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        maxAmountsIn = []#[1000000000000000000, 100000000000000000]

        constraints = context.agent.profile.action_configs['balancerv2vault_JoinPool'].constraints
       # if 'maxAmount0In' in constraints:
       #     maxAmountsIn = constraints['maxAmount0In']


        

        #------------------------------------------
        # ERC20 Approve
        #------------------------------------------
        # Get ERC20 client
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            logger.warning("ERC20 client not found in context")
            return {}
        
        for i, token_address in enumerate(assets):
            try:
                token_balance = erc20_client.balance_of(token_address, sender)
                if not token_balance > 0:
                    return {}

                maxAmountsIn.append(int(token_balance * random.uniform(0.1, 0.5)))
               
                tx = erc20_client.approve(
                    token_address=token_address,
                    spender=vault_address,
                    amount=token_balance, 
                    sender=sender,
                    value=0
                )
                if not tx:
                    logger.error(f"Approval failed for token {token_address}")
                    return {}
                logger.info(f"Successfully approved token {token_address}")
            except Exception as e:
                logger.error(f"Error during approval for token {token_address}: {e}")
                return {}

        # Prepare join parameters
        join_kind = 0  # INIT join kind
        userData = encode(['uint256', 'uint256[]'], [join_kind, maxAmountsIn])
        fromInternalBalance = False

        params['poolId'] = poolId
        params['sender_account'] = sender
        params['recipient'] = sender
        params['request'] = {
            'assets': assets,
            'maxAmountsIn': maxAmountsIn,
            'userData': userData,
            'fromInternalBalance': fromInternalBalance,
        }
        print(params)
        return params



class ManagePoolBalanceStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        # Initialize ops tuple fields
        ops_fields = {
            
            'kind': None,  # uint8
            
            'poolId': None,  # bytes32
            
            'token': None,  # address
            
            'amount': None,  # uint256
            
        }
        params['ops'] = ops_fields
        
        

        return params


class ManageUserBalanceStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        # Initialize ops tuple fields
        ops_fields = {
            
            'kind': None,  # uint8
            
            'asset': None,  # address
            
            'amount': None,  # uint256
            
            'sender': None,  # address
            
            'recipient': None,  # address
            
        }
        params['ops'] = ops_fields
        
        

        return params


class QueryBatchSwapStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['kind'] = None  # type: uint8
        
        
        
        
        # Initialize swaps tuple fields
        swaps_fields = {
            
            'poolId': None,  # bytes32
            
            'assetInIndex': None,  # uint256
            
            'assetOutIndex': None,  # uint256
            
            'amount': None,  # uint256
            
            'userData': None,  # bytes
            
        }
        params['swaps'] = swaps_fields
        
        
        
        
        params['assets'] = None  # type: address[]
        
        
        
        
        # Initialize funds tuple fields
        funds_fields = {
            
            'sender': None,  # address
            
            'fromInternalBalance': None,  # bool
            
            'recipient': None,  # address
            
            'toInternalBalance': None,  # bool
            
        }
        params['funds'] = funds_fields
        
        

        return params


class RegisterPoolStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['specialization'] = None  # type: uint8
        
        
        

        return params


class RegisterTokensStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['poolId'] = None  # type: bytes32
        
        
        
        
        
        params['tokens'] = None  # type: address[]
        
        
        
        
        
        params['assetManagers'] = None  # type: address[]
        
        
        

        return params


class SetAuthorizerStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['newAuthorizer'] = None  # type: address
        
        
        

        return params


class SetPausedStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['paused'] = None  # type: bool
        
        
        

        return params


class SetRelayerApprovalStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['sender_account'] = None  # type: address (renamed from 'sender')
        
        
        
        
        
        params['relayer'] = None  # type: address
        
        
        
        
        
        params['approved'] = None  # type: bool
        
        
        

        return params


class SwapStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        poolId = '0x8621d57c0e3a0b6dd1d7f8e9d7de1801c162dc960002000000000000000000ee'
        kind = 0
        assetIn = '0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252'
        assetOut = '0xE7EAb97CE3ed656DC40114d0b829A2D00F0edDB1'
        amount = int(110)
        userData = b''

        limit = 999999999999999999
        deadline = 999999999999999999
        

        singleSwap = {
            'poolId': poolId,  # bytes32
            'kind': kind,  # uint8
            'assetIn': assetIn,  # address
            'assetOut': assetOut,  # address
            'amount': amount,  # uint256
            'userData': userData,  # bytes
        }
        funds = {
            'sender': sender,  # address
            'fromInternalBalance': False,  # bool
            'recipient': sender,  # address
            'toInternalBalance': False,  # bool
        }

        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 100000            # Transaction value
        } 
       
        params['singleSwap'] = singleSwap
        params['funds'] = funds
        params['limit'] = limit  # type: uint256
        params['deadline'] = deadline  # type: uint256

        print(params)
        
        
        

        return params

