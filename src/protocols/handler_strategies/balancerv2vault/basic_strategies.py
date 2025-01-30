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

        vault_address = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        sender = self.get_sender(context)
        if not sender:
            logger.info("No sender found")
            return None


        # Get ERC20 client
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            logger.warning("ERC20 client not found in context")
            return {}

        # Define start and end tokens (keep original case for balance check)
        start_token = '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1'  # WETH
        end_token = '0xaf204776c7245bf4147c2612bf6e5972ee483701'    # sDAI
        
        logger.info(f"Looking for path from {start_token} to {end_token}")

        # Find path between tokens (path will contain lowercase addresses)
        path = context.find_swap_path(start_token, end_token)
        if not path:
            logger.warning(f"No path found between {start_token} and {end_token}")
            return {}

        logger.info(f"Found path: {path}")

        # Get balance of input token
        token_balance = erc20_client.balance_of(start_token, sender)
        logger.info(f"Token balance: {token_balance}")
        if token_balance == 0:
            logger.info("No balance available")
            return {}
        
        try:
            tx = erc20_client.approve(
                token_address=start_token,
                spender=vault_address,
                amount=token_balance, 
                sender=sender,
                value=0
            )
            if not tx:
                logger.error(f"Approval failed for token {start_token}")
                return {}
            logger.info(f"Successfully approved token {start_token}")
        except Exception as e:
            logger.error(f"Error during approval for token {start_token}: {e}")
            return {}

        # Calculate swap amount
        amount = int(token_balance * random.uniform(0.1, 0.9))

        # Build assets array - ensure all addresses are lowercase
        assets = []
        assets.append(start_token.lower())  # First token
        for hop in path:
            # Add the output token of each hop
            if hop['to_token'] not in assets:  # hop['to_token'] is already lowercase
                assets.append(hop['to_token'])

        logger.info(f"Assets array: {assets}")

        # Build swaps array
        swaps = []
        for i, hop in enumerate(path):
            try:
                swap = {
                    'poolId': hop['pool_id'],
                    'assetInIndex': assets.index(hop['from_token']),  
                    'assetOutIndex': assets.index(hop['to_token']),   
                    'amount': amount if i == 0 else 0,  
                    'userData': b''
                }
                swaps.append(swap)
                logger.info(f"Added swap {i}: from index {swap['assetInIndex']} to {swap['assetOutIndex']}")
            except ValueError as e:
                logger.error(f"Error creating swap {i}: {e}")
                logger.error(f"from_token: {hop['from_token']}")
                logger.error(f"to_token: {hop['to_token']}")
                logger.error(f"Available assets: {assets}")
                return {}

        # Set limits
        slippage = 0.05  # 5% slippage tolerance
        limits = []
        for i in range(len(assets)):
            if i == 0:  
                # For input token: set limit slightly higher than amount to account for fees
                limits.append(int(amount * (1 + slippage)))
            else:  
                # For output tokens: set minimum desired output to 0
                limits.append(0)

        # Initialize parameters with transaction details
        params = {
            'sender': sender,     
            'value': 0,           
            'kind': 0,            # GIVEN_IN
            'swaps': swaps,       
            'assets': assets,     
            'funds': {
                'sender': sender,
                'fromInternalBalance': False,
                'recipient': sender,
                'toInternalBalance': False
            },
            'limits': limits,
            'deadline': int(context.chain.blocks.head.timestamp + 3600)  # + 1 hour 
        }

        logger.info("Built batch swap parameters:")
        logger.info(f"Number of assets: {len(assets)}")
        logger.info(f"Number of swaps: {len(swaps)}")
        for i, swap in enumerate(swaps):
            logger.info(f"Swap {i}: Pool {swap['poolId']}")
            logger.info(f"  {assets[swap['assetInIndex']]} -> {assets[swap['assetOutIndex']]}")
            logger.info(f"  Amount: {swap['amount']}")

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
        poolId_list = [poolId for poolId in LBPs_state.keys() if LBPs_state[poolId]['owner']==sender]

        if not poolId_list:
            return {}

        poolId = random.choice(poolId_list)
        assets = LBPs_state[poolId]['tokens']
        vault_address = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        maxAmountsIn = []


        #------------------------------------------
        # ERC20 Approve
        #------------------------------------------
        # Get ERC20 client
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            logger.warning("ERC20 client not found in context")
            return {}
        
        for i, token_address in enumerate(assets):
            token_balance = erc20_client.balance_of(token_address, sender)
            if not token_balance > 0:
                return {}

            maxAmountsIn.append(token_balance)
               
        print(maxAmountsIn)

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
    
    def get_params2(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
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
        poolId_list = [poolId for poolId in LBPs_state.keys() if LBPs_state[poolId]['owner']==sender]

        if not poolId_list:
            return {}

        poolId = random.choice(poolId_list)
        assets = LBPs_state[poolId]['tokens']
        vault_address = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        maxAmountsIn = []

        constraints = context.agent.profile.action_configs['balancerv2vault_JoinPool'].constraints

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

        # Get ERC20 client
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            logger.warning("ERC20 client not found in context")
            return {}
        
        if not isinstance(context.network_state['contract_states'].get('BalancerV2LBPFactory'), dict):
            return {}
        
        LBPs_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']['LBPs']
        poolId = random.choice(list(LBPs_state.keys()))
        assets = LBPs_state[poolId]['tokens']
    
        kind = 0
        assetIn = assets[0]
        assetOut = assets[1]

        token_balance = erc20_client.balance_of(assetIn, sender)
        amount = int(token_balance * random.uniform(0.000000000001, 0.0001))
        userData = b''

        limit = 0
        deadline = 999999999999999999999

  
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
            'value': 0            # Transaction value
        } 
       
        params['singleSwap'] = singleSwap
        params['funds'] = funds
        params['limit'] = limit  # type: uint256
        params['deadline'] = deadline  # type: uint256

        return params

