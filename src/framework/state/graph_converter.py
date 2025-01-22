import pandas as pd
from typing import Dict, Any, Tuple
from ape_ethereum import Ethereum
from ape import chain
from src.framework.logging import get_logger
import logging
from datetime import datetime

logger = get_logger(__name__,logging.DEBUG)

def convert_to_demurrage(delta_days,balance):
    GAMMA = 0.9998013320085989574306134065681911664857225676913333806934
    return float(GAMMA**delta_days * balance)

class StateToGraphConverter:

    @staticmethod
    def convert_state_to_dataframes(state: Dict[str, Any], 
                                  current_time: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Convert state to trust and balance dataframes"""
        
        # Trust DataFrame creation - this part works fine
        trust_pairs = []
        trust_markers = state.get('trustMarkers', {})
        
        for truster, trustees in trust_markers.items():
            for trustee, expiry in trustees.items():
                if expiry > current_time:
                    trust_pairs.append({
                        'truster': str(truster),
                        'trustee': str(trustee)
                    })

        df_trusts = pd.DataFrame(trust_pairs, columns=['truster', 'trustee'])
        logger.info(f"\nCreated trusts DataFrame with {len(df_trusts)} rows")


        # Debug token balances structure
        token_balances = state.get('token_balances', {})
        
        # Create balances DataFrame - modified to handle token_id correctly
        balance_records = []
        
        

        for account, tokens in token_balances.items():
            for token_id, balance_info in tokens.items():
                balance = balance_info['balance']
                last_day_updated = balance_info['last_day_updated']
                current_day = datetime.fromtimestamp(current_time).date()
                delta_days = (current_day - last_day_updated).days

                if balance > 0:
                    # For each token held by an account, need an entry
                    try:
                        token_address = Ethereum.decode_address(token_id)
                        balance_records.append({
                            'account': str(account),
                            'tokenAddress': str(token_address), 
                            'demurragedTotalBalance': convert_to_demurrage(delta_days,balance)
                        })
                    except Exception as e:
                        logger.error(f"Error processing balance for {account}, token {token_id}: {e}")

        df_balances = pd.DataFrame(balance_records, 
                                 columns=['account', 'tokenAddress', 'demurragedTotalBalance'])
        logger.info(f"Created balances DataFrame with {len(df_balances)} rows")
        
        return df_trusts, df_balances