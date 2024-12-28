from typing import Dict, Optional, Callable, Any
from datetime import datetime
import logging
from ape import chain
from src.framework.logging import get_logger

logger = get_logger(__name__)

class NetworkComponent:
    """
    Base class for network components with event handling.
    Provides a standardized way to handle events across the system.
    """
    
    def __init__(self):
        """Initialize base event handlers"""
        # Core event handlers
        self._event_handlers = {
            'human_registered': None,
            'trust_created': None,
            'mint_performed': None,
            'transfer_performed': None,
            'group_created': None,
            'error_occurred': None,
            'state_changed': None,

            'transfer': None,
            'trust': None,
            'mint': None,
            'agent_action': None,
            'agent_created': None,
            'stop_minting': None, 
            'wrap_token': None,
            'error': None
        }
        
        # Event statistics tracking
        self._event_stats = {
            'human_registered': 0,
            'trust_created': 0,
            'mint_performed': 0,
            'transfer_performed': 0,
            'group_created': 0,
            'errors': 0
        }
        
        # Component state
        self._active = True
        self._error_count = 0
        self._last_event_time = None

    def register_event_handlers(self, handlers: Dict[str, Callable]):
        """
        Register multiple event handlers at once.
        
        Args:
            handlers: Dictionary mapping event names to handler functions
        """
        try:
            for event_name, handler in handlers.items():
                if event_name in self._event_handlers:
                    if not callable(handler) and handler is not None:
                        raise ValueError(f"Handler for {event_name} must be callable or None")
                    self._event_handlers[event_name] = handler
                else:
                    logger.warning(f"Unknown event type: {event_name}")
        except Exception as e:
            logger.error(f"Failed to register event handlers: {e}")
            self._handle_error("register_handlers", e)

    def register_handler(self, event_name: str, handler: Optional[Callable]):
        """
        Register a single event handler.
        
        Args:
            event_name: Name of the event to handle
            handler: Callback function for the event
        """
        try:
            if event_name in self._event_handlers:
                if not callable(handler) and handler is not None:
                    raise ValueError(f"Handler for {event_name} must be callable or None")
                self._event_handlers[event_name] = handler
            else:
                logger.warning(f"Unknown event type: {event_name}")
        except Exception as e:
            logger.error(f"Failed to register handler for {event_name}: {e}")
            self._handle_error("register_handler", e)

    def _emit_event(self, event_name: str, *args, **kwargs):
        """
        Emit an event to registered handler.
        
        Args:
            event_name: Name of the event to emit
            *args: Positional arguments for the handler
            **kwargs: Keyword arguments for the handler
        """
        try:
            handler = self._event_handlers.get(event_name)
            if handler:
                # Add standard event metadata
                kwargs['timestamp'] = kwargs.get('timestamp', chain.blocks.head.timestamp)
                kwargs['block_number'] = kwargs.get('block_number', chain.blocks.head.number)
                
                # Call handler
                handler(*args, **kwargs)
                
                # Update statistics
                self._event_stats[event_name] = self._event_stats.get(event_name, 0) + 1
                self._last_event_time = datetime.now()
        except Exception as e:
            logger.error(f"Error emitting event {event_name}: {e}")
            self._handle_error("emit_event", e)

    def _handle_error(self, context: str, error: Exception):
        """
        Handle component errors uniformly.
        
        Args:
            context: String describing where the error occurred
            error: The exception that was raised
        """
        self._error_count += 1
        error_handler = self._event_handlers.get('error_occurred')
        
        if error_handler:
            try:
                error_handler(context, error)
            except Exception as e:
                logger.error(f"Error handler failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get component statistics and state.
        
        Returns:
            Dictionary containing event counts and component state
        """
        return {
            'events': self._event_stats.copy(),
            'error_count': self._error_count,
            'active': self._active,
            'last_event': self._last_event_time
        }

    # Protected event emission methods for subclasses
    
    def _emit_human_registered(self, address: str, inviter: Optional[str] = None, **kwargs):
        """Emit human registered event"""
        self._emit_event('human_registered', address=address, inviter=inviter, **kwargs)

    def _emit_trust_created(self, truster: str, trustee: str, limit: int, **kwargs):
        """Emit trust created event"""
        self._emit_event('trust_created', truster=truster, trustee=trustee, 
                        limit=limit, **kwargs)

    def _emit_mint_performed(self, address: str, amount: int, **kwargs):
        """Emit mint performed event"""
        self._emit_event('mint_performed', address=address, amount=amount, **kwargs)

    def _emit_transfer_performed(self, from_addr: str, to_addr: str, 
                               amount: int, **kwargs):
        """Emit transfer performed event"""
        self._emit_event('transfer_performed', from_address=from_addr,
                        to_address=to_addr, amount=amount, **kwargs)

    def _emit_group_created(self, creator: str, group_addr: str, 
                          name: str, **kwargs):
        """Emit group created event"""
        self._emit_event('group_created', creator=creator, 
                        group_address=group_addr, name=name, **kwargs)

    def _emit_state_changed(self, old_state: Dict, new_state: Dict, **kwargs):
        """Emit state changed event"""
        self._emit_event('state_changed', old_state=old_state, 
                        new_state=new_state, **kwargs)