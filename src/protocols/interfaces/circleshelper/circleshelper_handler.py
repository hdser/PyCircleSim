import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.circleshelper.circleshelper_client import (
    CirclesHelperClient,
)
