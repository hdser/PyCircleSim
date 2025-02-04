from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ExecutionResult:
    """Result of an implementation execution"""
    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
@dataclass 
class GasEstimate:
    """Gas estimation for an implementation"""
    total: int
    breakdown: Dict[str, int]