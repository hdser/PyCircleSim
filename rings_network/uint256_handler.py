from typing import Union
from decimal import Decimal

class UINT256Handler:
    """Handler for large numbers that preserves full precision"""
    
    @staticmethod
    def to_string(value: Union[int, str, float, Decimal]) -> str:
        """Convert any value to a full precision string representation"""
        if isinstance(value, str):
            # Handle hex strings from Ape
            if value.startswith('0x'):
                return str(int(value, 16))
            return value
            
        if isinstance(value, int):
            return str(value)
            
        if isinstance(value, float) or isinstance(value, Decimal):
            # Convert to Decimal for maximum precision
            return str(Decimal(str(value)))
        
        raise ValueError(f"Unsupported value type: {type(value)}")

    @staticmethod
    def to_wei(value: Union[int, str, float, Decimal]) -> str:
        """Convert to wei representation as string"""
        if isinstance(value, (float, int)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            value = Decimal(value)
        
        # Convert to wei (18 decimals)
        return str(int(value * Decimal("1000000000000000000")))

    @staticmethod
    def from_wei(value: Union[str, int]) -> Decimal:
        """Convert wei value back to decimal"""
        if isinstance(value, str):
            if value.startswith('0x'):
                value = int(value, 16)
            else:
                value = int(value)
        return Decimal(str(value)) / Decimal("1000000000000000000")