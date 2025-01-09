from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
import os
import re
from jinja2 import Environment, FileSystemLoader
import logging
import black
import ast

logger = logging.getLogger(__name__)

class ContractFunction:
    PYTHON_KEYWORDS = {
        'from', 'to', 'in', 'import', 'class', 'def', 'return', 'pass', 
        'raise', 'global', 'assert', 'lambda', 'yield', 'del'
    }

    def __init__(self, abi_entry: Dict):
        self.name = abi_entry.get('name', '')
        self.inputs = abi_entry.get('inputs', [])
        self.outputs = abi_entry.get('outputs', [])
        self.stateMutability = abi_entry.get('stateMutability', '')
        self.type = abi_entry.get('type', '')
        self.is_view = self.stateMutability in ['view', 'pure']

    def get_python_params(self) -> str:
        """Get parameters as a string suitable for both function definition and calling"""
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name in self.PYTHON_KEYWORDS:
                param_name = f"{param_name}_"
            param_type = self._get_python_type(inp['type'])
            params.append(param_name)
        return ", ".join(params)
    
    def get_python_param_defs(self) -> str:
        """Get parameter definitions for function signatures"""
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name in self.PYTHON_KEYWORDS:
                param_name = f"{param_name}_"
            param_type = self._get_python_type(inp['type'])
            params.append(f"{param_name}: {param_type}")
        return ", ".join(params)

    def get_safe_param_name(self, name: str) -> str:
        """Get parameter name that's safe to use in Python"""
        if not name:
            return name
        return f"{name}_" if name in self.PYTHON_KEYWORDS else name

    def get_input_names(self) -> List[Tuple[str, str]]:
        """Get list of (original_name, safe_name) tuples for all inputs"""
        return [
            (inp.get('name', f'param{i}'), self.get_safe_param_name(inp.get('name', f'param{i}')))
            for i, inp in enumerate(self.inputs)
        ]

    def get_python_return_type(self) -> str:
        if not self.outputs:
            return 'bool'
        elif len(self.outputs) == 1:
            return self._get_python_type(self.outputs[0]['type'])
        else:
            types = [self._get_python_type(out['type']) for out in self.outputs]
            return f"Tuple[{', '.join(types)}]"

    def _get_python_type(self, sol_type: str) -> str:
        type_map = {
            'address': 'str',
            'uint256': 'int',
            'uint96': 'int',
            'uint64': 'int',
            'uint16': 'int',
            'int256': 'int',
            'bytes32': 'bytes',
            'bytes': 'bytes',
            'string': 'str',
            'bool': 'bool'
        }
        
        # Handle arrays
        if '[]' in sol_type:
            base_type = sol_type.replace('[]', '')
            return f"List[{self._get_python_type(base_type)}]"
            
        return type_map.get(sol_type, 'Any')

class ContractEvent:
    def __init__(self, abi_entry: Dict):
        self.name = abi_entry.get('name', '')
        self.inputs = abi_entry.get('inputs', [])
        self.indexed = [inp.get('indexed', False) for inp in self.inputs]


def format_action_name(name: str) -> str:
    """Convert function name to action format (e.g. registerHuman -> REGISTER_HUMAN)"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.upper()

def to_camel_case(name: str) -> str:
    """Convert function name to CamelCase"""
    # For function names 
    if any(c.isupper() for c in name):
        # Already has some capitalization, preserve it
        words = []
        current = []
        for c in name:
            if c.isupper() and current:
                words.append(''.join(current))
                current = []
            current.append(c)
        if current:
            words.append(''.join(current))
        return ''.join(w.capitalize() for w in words)
    else:
        # Simple underscore case
        return ''.join(word.capitalize() for word in name.split('_'))
    
class ContractGenerator:
    def __init__(self, abi_path: str, templates_dir: str = "templates", project_root: Path = None):
        self.abi_path = Path(abi_path)
        self.project_root = project_root or Path(__file__).parents[2]
        self.protocols_dir = self.project_root / "src" / "protocols"
        self.framework_dir = self.project_root / "src" / "framework"

        # Extract name from ABI or directory
        name = self.abi_path.stem
        if name.startswith('0x'):
            parent_dir = self.abi_path.parent.name
            self.contract_name = parent_dir.capitalize()
        else:
            self.contract_name = name

        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.env.filters['camel_case'] = to_camel_case

        with open(abi_path) as f:
            self.abi = json.load(f)
            
        self.functions = []
        self.events = []
        self._parse_abi()

    def _parse_abi(self):
        for entry in self.abi:
            if entry['type'] == 'function':
                self.functions.append(ContractFunction(entry))
            elif entry['type'] == 'event':
                self.events.append(ContractEvent(entry))

    def generate_all(self):
        """Generate all contract interfaces and strategies"""
        # Create interface directory 
        interface_dir = self.protocols_dir / "interfaces" / self.contract_name.lower()
        interface_dir.mkdir(parents=True, exist_ok=True)

        # Create handler strategies directory
        strategies_dir = self.protocols_dir / "handler_strategies" / self.contract_name.lower()
        strategies_dir.mkdir(parents=True, exist_ok=True)

        # Generate client and handler
        self.generate_client(interface_dir)
        self.generate_handler(interface_dir)
        self.generate_interface_init(interface_dir)
        self.generate_strategies(strategies_dir)

    def generate_interface_init(self, output_dir: Path):
        """Generate __init__.py for interface directory"""
        template = self.env.get_template('interface_init.py.j2')
        
        # Get handler classes for non-view functions
        handlers = [f.name for f in self.functions if not f.is_view]
        
        content = template.render(
            contract_name=self.contract_name,
            handlers=[to_camel_case(h) + "Handler" for h in handlers]
        )
        
        output_path = output_dir / "__init___template.py"
        self._write_formatted_python(content, output_path)
        

    def generate_client(self, output_dir: str):
        """Generate client interface"""
        template = self.env.get_template('client.py.j2')
        
        content = template.render(
            contract_name=self.contract_name,
            functions=self.functions,
            events=self.events
        )
        
        output_path = Path(output_dir) / f"{self.contract_name.lower()}_client_template.py"
        self._write_formatted_python(content, output_path)

    def generate_handler(self, output_dir: str):
        """Generate action handlers"""
        template = self.env.get_template('handler.py.j2')
        
        # Only generate handlers for non-view functions
        action_functions = [f for f in self.functions if not f.is_view]
        
        content = template.render(
            contract_name=self.contract_name,
            functions=action_functions
        )
        
        # Output path now includes 'actions' in name
        output_path = Path(output_dir) / f"{self.contract_name.lower()}_handler_template.py"
        self._write_formatted_python(content, output_path)

    def generate_strategies(self, output_dir: Path):
        """Generate strategy files"""
        # Generate basic strategies
        template = self.env.get_template('basic_strategies.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            functions=self.functions
        )
        output_path = output_dir / "basic_strategies_template.py"
        self._write_formatted_python(content, output_path)

        # Generate init file
        template = self.env.get_template('__init__.py.j2')
        content = template.render(
            functions=self.functions
        )
        output_path = output_dir / "__init___template.py"
        self._write_formatted_python(content, output_path)

    def _write_formatted_python(self, content: str, path: Path):
        """Write formatted Python code, skipping Black formatting for template files"""
        try:
            # Skip Black formatting for template files
            if path.name.endswith('_template.py'):
                # Just write the content directly for templates
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                logger.info(f"Wrote unformatted template to {path}")
            else:
                # For non-template files, apply Black formatting
                formatted = black.format_str(content, mode=black.FileMode())
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(formatted)
                logger.info(f"Wrote formatted Python code to {path}")
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            # Write unformatted as fallback
            path.write_text(content)


def generate_contract_interfaces(abi_path: str, output_dir: str, templates_dir: str):
    """Main generator function"""
    generator = ContractGenerator(abi_path, templates_dir)
    
    generator.generate_client(output_dir)
    generator.generate_handler(output_dir)

if __name__ == "__main__":
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("abi_path", help="Path to contract ABI JSON")
   parser.add_argument("--templates-dir", default="templates", help="Templates directory") 
   args = parser.parse_args()
   
   generator = ContractGenerator(args.abi_path, args.templates_dir)
   generator.generate_all()