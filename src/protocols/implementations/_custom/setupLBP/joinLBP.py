from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from ape_ethereum.ecosystem import encode
import random


@register_implementation("custom_joinLBP")
class JoinLBP(BaseImplementation):

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
       
        sender = context.acting_address
       
        client = context.get_client("balancerv2vault")
        if not client:
            return []

        if not isinstance(context.network_state['contract_states'].get('BalancerV2LBPFactory'), dict):
            return []
        
        if not isinstance(context.network_state['contract_states']['BalancerV2LBPFactory'].get('state'), dict):
            return []

        if not isinstance(context.network_state['contract_states']['BalancerV2LBPFactory']['state'].get('LBPs'), dict):
            return []

        LBPs_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']['LBPs']
        poolId_list = [poolId for poolId in LBPs_state.keys() if LBPs_state[poolId]['owner']==sender]

        if not poolId_list:
            return []

        poolId = random.choice(poolId_list)
        assets = LBPs_state[poolId]['tokens']
        if assets[0].lower() > assets[1].lower():
            assets = assets[::-1]

        maxAmountsIn = []


        # Get ERC20 client
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            return []
        
        for i, token_address in enumerate(assets):
            token_balance = erc20_client.balance_of(token_address, sender)
            if not token_balance > 0:
                return []

            maxAmountsIn.append(token_balance)
               

        # Prepare join parameters
        join_kind = 0  # INIT join kind
        userData = encode(['uint256', 'uint256[]'], [join_kind, maxAmountsIn])
        fromInternalBalance = False


        request = {
            'assets': assets,
            'maxAmountsIn': maxAmountsIn,
            'userData': userData,
            'fromInternalBalance': fromInternalBalance,
        }

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="joinPool",
                params={
                    "sender": sender,
                    "value": 0,
                    "poolId": poolId,
                    "sender_account": sender,
                    "recipient": sender,
                    "request": request,
                },
            )
        ]
