from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
import random

logger = get_logger(__name__)

class LBPSetupStrategy(BaseStrategy):
    """Strategy for generating multicall transactions"""

    
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        """Generate parameters for a multicall swap through Balancer pools"""
        sender = self.get_sender(context)
        if not sender:
            logger.warning("No sender address available")
            return None

        # Define constants 
        VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
        MULTICALL_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"
        WXDAI_ADDRESS = "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d"
        WETH_ADDRESS = "0x6a023ccd1ff6f2045c3309768ead9e68f978f6e1"
        
        # Amount to swap
        amount = int(0.0001e18)

        # Get path between tokens
        path = context.find_swap_path(WXDAI_ADDRESS, WETH_ADDRESS)
        if not path:
            logger.warning(f"No path found between WXDAI and WETH")
            return None

        logger.info(f"Found path: {path}")

        # Build assets array
        assets = []
        assets.append(WXDAI_ADDRESS.lower())
        for hop in path:
            if hop['to_token'] not in assets:
                assets.append(hop['to_token'])
        logger.info(f"Assets array: {assets}")

        # Build swaps array
        swaps = []
        for i, hop in enumerate(path):
            swap = {
                'poolId': hop['pool_id'],
                'assetInIndex': assets.index(hop['from_token']),
                'assetOutIndex': assets.index(hop['to_token']),
                'amount': amount if i == 0 else 0,
                'userData': b''
            }
            swaps.append(swap)
            logger.info(f"Added swap {i}: {hop['from_token']} -> {hop['to_token']}")

        # Set limits with slippage
        slippage = 0.05
        limits = []
        for i in range(len(assets)):
            if i == 0:
                limits.append(int(amount * (1 + slippage)))
            else:
                limits.append(0)

        # Set up direct approvals first
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            logger.warning("ERC20 client not found")
            return None

        # Approve both Vault and Multicall contract
        for spender in [VAULT_ADDRESS, MULTICALL_ADDRESS]:
            try:
                tx = erc20_client.approve(
                    token_address=WXDAI_ADDRESS,
                    spender=spender,
                    amount=int(amount * 2),  # Double the amount for safety
                    sender=sender,
                    value=0
                )
                if not tx:
                    logger.error(f"Failed to approve {spender}")
                    return None
                logger.info(f"Approved {spender} to spend WXDAI")
            except Exception as e:
                logger.error(f"Approval failed for {spender}: {e}")
                return None

        # Build multicall sequence
        multicall_params = {
            "tx_params": {
                "sender": sender,
                "value": 0,
                "allow_failure": False
            }
        }

        # Add relayer approval
        multicall_params['balancerv2vault_setRelayerApproval'] = {
            'sender_account': sender,
            'relayer': MULTICALL_ADDRESS,
            'approved': True,
            'allow_failure': False
        }

        # Add batch swap
        multicall_params['balancerv2vault_batchSwap'] = {
            'kind': 0,  # GIVEN_IN
            'swaps': swaps,
            'assets': assets,
            'funds': {
                'sender': sender,
                'fromInternalBalance': False,
                'recipient': sender,
                'toInternalBalance': False
            },
            'limits': limits,
            'deadline': int(context.chain.blocks.head.timestamp + 3600)
        }

        logger.info("Prepared multicall sequence:")
        logger.info("1. Direct token approvals completed")
        logger.info("2. Setting relayer approval")
        logger.info(f"3. Executing batch swap through {len(swaps)} pools")
        logger.info(f"Total input amount: {amount / 1e18} WXDAI")

        return multicall_params