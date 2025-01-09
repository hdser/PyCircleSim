from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import importlib
import inspect
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.framework.logging import get_logger

logger = get_logger(__name__)

@dataclass
class ActionMetadata:
    """Metadata about an action handler"""
    name: str                    # Full action name (e.g. ringshub_PersonalMint)
    handler_class: str           # Handler class name
    module_path: str            # Full module path
    constraints: List[str]      # Supported constraints
    required_params: List[str]  # Required parameters
    module_name: str           # Module name without _handler (e.g. ringshub)

class ActionRegistry:
    """Central registry of available actions"""
    
    def __init__(self):
        self._actions: Dict[str, ActionMetadata] = {}
        self._template_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / 'actions_generator' / 'templates')
        )
        
    def discover_actions(self, protocols_dir: str):
        """Auto-discover action handlers from protocol interfaces"""
        protocols_path = Path(protocols_dir)
        if not protocols_path.exists():
            logger.error(f"Protocols directory not found: {protocols_dir}")
            return

        # Look specifically in the interfaces directory
        interfaces_path = protocols_path / "interfaces"
        if not interfaces_path.exists():
            logger.error(f"Interfaces directory not found: {interfaces_path}")
            return

        for interface_dir in interfaces_path.iterdir():
            if not interface_dir.is_dir() or interface_dir.name.startswith('_'):
                continue
            
            module_name = interface_dir.name
            self._register_handlers_from_interface(module_name)

    def _register_handlers_from_interface(self, module_name: str):
        """Extract and register handlers from an interface module"""
        try:
            interface_path = f"src.protocols.interfaces.{module_name}"
            module = importlib.import_module(interface_path)
            
            # Get handler classes from the module's __all__ attribute
            handler_classes = [
                name for name in module.__all__ 
                if name.endswith('Handler') and not name.endswith('BaseHandler')
            ]
            
            for handler_name in handler_classes:
                handler_class = getattr(module, handler_name)
                
                # Create action name
                action_name = f"{module_name}_{handler_name[:-7]}"
                
                metadata = ActionMetadata(
                    name=action_name,
                    handler_class=handler_name,
                    module_path=interface_path,
                    constraints=self._extract_constraints(handler_class),
                    required_params=self._extract_params(handler_class),
                    module_name=module_name
                )
                
                self._actions[action_name] = metadata
                logger.info(f"Registered action {action_name} from {interface_path}")
                    
        except Exception as e:
            logger.error(f"Error registering handlers from {module_name}: {e}", exc_info=True)


    def _register_handlers_from_file(self, handler_file: Path, module_name: str):
        """Extract and register handlers from a file"""
        try:
            # Determine module path for interfaces structure
            interface_path = f"src.protocols.interfaces.{module_name}"
            module = importlib.import_module(interface_path)
                
            # Find handler classes from the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    name.endswith('Handler') and 
                    hasattr(obj, 'execute')):
                    
                    # Create action name with module prefix
                    action_name = f"{module_name}_{name[:-7]}"  # Remove 'Handler'
                    
                    metadata = ActionMetadata(
                        name=action_name,
                        handler_class=name,
                        module_path=interface_path,
                        constraints=self._extract_constraints(obj),
                        required_params=self._extract_params(obj),
                        module_name=module_name
                    )
                    
                    self._actions[action_name] = metadata
                    logger.debug(f"Registered action {action_name} from {interface_path}")
                        
        except Exception as e:
            logger.error(f"Error registering handlers from {module_name}: {e}")
                
                    
    def _extract_constraints(self, handler_class) -> List[str]:
        """Extract supported constraints from handler class"""
        constraints = []
        
        # Check class docstring for @constraints decorator
        if handler_class.__doc__:
            for line in handler_class.__doc__.split('\n'):
                if '@constraint' in line:
                    constraint = line.split('@constraint')[-1].strip()
                    constraints.append(constraint)
                    
        # Check _get_params method for constraints in template
        if hasattr(handler_class, '_get_params'):
            params_method = handler_class._get_params
            if params_method.__doc__:
                for line in params_method.__doc__.split('\n'):
                    if 'constraints:' in line:
                        constraint = line.split('constraints:')[-1].strip()
                        constraints.append(constraint)
                        
        return constraints
        
    def _extract_params(self, handler_class) -> List[str]:
        """Extract required parameters from handler's _get_params method"""
        params = []
        
        if hasattr(handler_class, '_get_params'):
            # Get source code of _get_params
            source = inspect.getsource(handler_class._get_params)
            
            # Look for required params in template dict
            for line in source.split('\n'):
                if "': None" in line:  # Template parameter
                    param = line.split("'")[1]
                    params.append(param)
                    
        return params
        
    def generate_action_types(self, output_file: str):
        """Generate ActionType enum class"""
        template = self._template_env.get_template('action_types.py.j2')
        
        content = template.render(
            actions=sorted(self._actions.keys())
        )
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Generated action types in {output_file}")
        
    def get_metadata(self, action_name: str) -> Optional[ActionMetadata]:
        """Get metadata for an action"""
        return self._actions.get(action_name)
        
    def validate_action_config(self, action_name: str, config: Dict[str, Any]) -> List[str]:
        """Validate action configuration against metadata"""
        errors = []
        metadata = self.get_metadata(action_name)
        
        if not metadata:
            errors.append(f"Unknown action: {action_name}")
            return errors
            
        # Check required params
        for param in metadata.required_params:
            if param not in config:
                errors.append(f"Missing required parameter: {param}")
                
        # Check constraints
        constraints = config.get('constraints', {})
        for constraint in constraints:
            if constraint not in metadata.constraints:
                errors.append(f"Invalid constraint: {constraint}")
                
        return errors