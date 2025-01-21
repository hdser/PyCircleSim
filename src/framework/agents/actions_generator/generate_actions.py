import sys
from pathlib import Path
import yaml
from ....framework.agents.action_registry import ActionRegistry
from src.framework.logging import get_logger

logger = get_logger(__name__)

def main():
    """Generate action types and validate configurations"""
    try:
        # Initialize registry
        registry = ActionRegistry()
        
        # Discover actions from protocols
        protocols_dir = Path(__file__).parents[4] / "src" / "protocols"
        registry.discover_actions(str(protocols_dir))
        
        # Generate action types
        types_file = Path(__file__).parents[1] / "types_template.py"
        registry.generate_action_types(str(types_file))
        
        # Validate agent config if provided
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
            validate_config(registry, config_file)
            
    except Exception as e:
        logger.error(f"Error generating actions: {e}")
        sys.exit(1)

def validate_config(registry: ActionRegistry, config_file: str):
    """Validate agent configuration file"""
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
            
        has_errors = False
        
        # Validate each profile's actions
        for profile_name, profile in config.get('profiles', {}).items():
            for action in profile.get('available_actions', []):
                action_name = action['action']
                errors = registry.validate_action_config(action_name, action)
                
                if errors:
                    has_errors = True
                    logger.error(f"\nProfile {profile_name}, Action {action_name}:")
                    for error in errors:
                        logger.error(f"  - {error}")
                        
        if has_errors:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error validating config: {e}")

if __name__ == "__main__":
    main()