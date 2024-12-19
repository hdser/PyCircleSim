from .registry import ActionRegistry, ActionConfig, action_registry
from .base import Action, ProtocolHandler, BaseProtocolAction
from .handlers.rings_handler import RingsHandler
from .handlers.fjord_handler import FjordHandler
from .protocols.rings_actions import (
    RingsAction,
    MintAction,
    TrustAction,
    TransferAction,
    CreateGroupAction
)
from .protocols.fjord_actions import (
    FjordAction,
    CreatePoolAction,
    ExitPoolAction,
    CreateWeightedPoolAction,
    SetSwapEnabledAction
)

__all__ = [
    'ActionRegistry',
    'ActionConfig',
    'action_registry',
    'Action',
    'ProtocolHandler',
    'BaseProtocolAction',
    'RingsHandler',
    'FjordHandler',
    'RingsAction',
    'FjordAction',
    # Rings actions
    'MintAction',
    'TrustAction',
    'TransferAction',
    'CreateGroupAction',
    # Fjord actions
    'CreatePoolAction',
    'ExitPoolAction',
    'CreateWeightedPoolAction',
    'SetSwapEnabledAction'
]

def initialize_handlers(rings_client=None, fjord_client=None):
    """Initialize protocol handlers with their respective clients"""
    if rings_client:
        action_registry.register_handler("rings", RingsHandler(rings_client))
    if fjord_client:
        action_registry.register_handler("fjord", FjordHandler(fjord_client))