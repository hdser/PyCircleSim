from typing import Dict, List
import pandas as pd
from datetime import datetime
import json

class DataCollector:
    """
    Responsible for collecting and storing network state data over time.
    """
    
    def __init__(self, analyzer):
        """
        Initialize the DataCollector.
        
        Args:
            analyzer: NetworkAnalyzer instance to use for data collection
        """
        self.analyzer = analyzer
        self.balance_history = []
        self.trust_history = []
        self.timestamps = []
        
    def collect_state(self, accounts, timestamp: int = None) -> None:
        """
        Collect current network state and store it.
        
        Args:
            accounts: List of accounts to collect data for
            timestamp: Optional timestamp for the collection
        """
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
            
        balance_df, trust_df = self.analyzer.analyze_network(accounts)
        
        self.balance_history.append(balance_df)
        self.trust_history.append(trust_df)
        self.timestamps.append(timestamp)
        
    def export_data(self, filepath: str) -> None:
        """
        Export collected data to file.
        
        Args:
            filepath: Path to save the data to
        """
        data = {
            'timestamps': self.timestamps,
            'balance_history': [df.to_dict() for df in self.balance_history],
            'trust_history': [df.to_dict() for df in self.trust_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
    def load_data(self, filepath: str) -> None:
        """
        Load previously collected data from file.
        
        Args:
            filepath: Path to load the data from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.timestamps = data['timestamps']
        self.balance_history = [pd.DataFrame.from_dict(d) for d in data['balance_history']]
        self.trust_history = [pd.DataFrame.from_dict(d) for d in data['trust_history']]
        
    def get_balance_timeseries(self, account: str) -> pd.Series:
        """
        Get balance history for a specific account.
        
        Args:
            account: Account to get history for
            
        Returns:
            pd.Series: Time series of account balances
        """
        balances = [df[df['Account'] == account]['Balance'].iloc[0] 
                   for df in self.balance_history]
        return pd.Series(balances, index=self.timestamps)
        
    def get_trust_evolution(self, truster: str, trustee: str) -> pd.Series:
        """
        Get trust relationship history between two accounts.
        
        Args:
            truster: Account that might trust
            trustee: Account that might be trusted
            
        Returns:
            pd.Series: Time series of trust status
        """
        trust_values = [df.loc[truster, trustee] for df in self.trust_history]
        return pd.Series(trust_values, index=self.timestamps)