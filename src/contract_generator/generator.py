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
        """Get parameters for both function definition and calling"""
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name in self.PYTHON_KEYWORDS:
                param_name = f"{param_name}_"
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
        """Get Python-safe parameter name"""
        if not name:
            return name
        return f"{name}_" if name in self.PYTHON_KEYWORDS else name

    def get_input_names(self) -> List[Tuple[str, str]]:
        """Get (original_name, safe_name) tuples for inputs"""
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
        
        if '[]' in sol_type:
            base_type = sol_type.replace('[]', '')
            return f"List[{self._get_python_type(base_type)}]"
            
        return type_map.get(sol_type, 'Any')

    def get_renamed_param_defs(self) -> str:
        """Get parameter definitions with renames for function signatures"""
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name == 'sender':
                param_name = 'sender_account'
            elif param_name == 'value':
                param_name = 'value_amount'
            elif param_name in self.PYTHON_KEYWORDS:
                param_name = f"{param_name}_"
            params.append(f"{param_name}: {self._get_python_type(inp['type'])}")
        return ", ".join(params)
    
    def get_safe_params(self) -> str:
        """Get safe parameter list for function calls"""
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name == 'sender':
                params.append('sender_')
            elif param_name == 'value':
                params.append('value_')
            elif param_name in self.PYTHON_KEYWORDS:
                params.append(f"{param_name}_")
            else:
                params.append(param_name)
        return ", ".join(params)

class ContractEvent:
    def __init__(self, abi_entry: Dict):
        self.name = abi_entry.get('name', '')
        self.inputs = abi_entry.get('inputs', [])
        self.indexed = [inp.get('indexed', False) for inp in self.inputs]

def format_action_name(name: str) -> str:
    """Convert to action format (camelCase -> CAMEL_CASE)"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.upper()

def to_camel_case(name: str) -> str:
    """Convert to CamelCase"""
    if any(c.isupper() for c in name):
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
        return ''.join(word.capitalize() for word in name.split('_'))

class ContractGenerator:
    def __init__(self, abi_path: str, templates_dir: str = "templates", project_root: Path = None):
        self.abi_path = Path(abi_path)
        self.project_root = project_root or Path(__file__).parents[2]
        self.protocols_dir = self.project_root / "src" / "protocols"

        name = self.abi_path.stem
        if name.startswith('0x'):
            parent_dir = self.abi_path.parent.name
            self.contract_name = to_camel_case(parent_dir)
        else:
            self.contract_name = to_camel_case(name)

        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.env.filters['camel_case'] = to_camel_case
        self.env.filters['safe_param_name'] = self._safe_param_name

        with open(abi_path) as f:
            self.abi = json.load(f)
            
        self.functions = []
        self.events = []
        self._parse_abi()

    @staticmethod
    def _safe_param_name(name: str) -> str:
        """Template filter for safe parameter names"""
        if name == 'sender':
            return 'account'
        if name in ['from', 'to', 'in', 'import', 'class', 'def', 'return', 'pass']:
            return f"{name}_"
        return name

    def _parse_abi(self):
        """Parse contract ABI into functions and events"""
        for entry in self.abi:
            if entry['type'] == 'function':
                self.functions.append(ContractFunction(entry))
            elif entry['type'] == 'event':
                self.events.append(ContractEvent(entry))

    def generate_all(self):
        """Generate all contract interfaces and implementations"""
        interface_dir = self.protocols_dir / "interfaces" / self.contract_name.lower()
        implementations_dir = self.protocols_dir / "implementations" / self.contract_name.lower()
        
        interface_dir.mkdir(parents=True, exist_ok=True)
        implementations_dir.mkdir(parents=True, exist_ok=True)

        self.generate_client(interface_dir)
        self.generate_handler(interface_dir)
        self.generate_interface_init(interface_dir)
        self.generate_implementations(implementations_dir)
        self.generate_main_implementations_init()

    def _append_template(self, path: Path) -> Path:
        """Append _template to filename"""
        return path.parent / f"{path.stem}_template{path.suffix}"

    def generate_client(self, output_dir: str):
        """Generate client interface"""
        template = self.env.get_template('client.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            functions=self.functions,
            events=self.events
        )
        output_path = self._append_template(Path(output_dir) / f"{self.contract_name.lower()}_client.py")
        self._write_formatted_python(content, output_path)

    def generate_handler(self, output_dir: str):
        """Generate action handlers"""
        action_functions = [f for f in self.functions if not f.is_view]
        template = self.env.get_template('handler.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            functions=action_functions
        )
        output_path = self._append_template(Path(output_dir) / f"{self.contract_name.lower()}_handler.py")
        self._write_formatted_python(content, output_path)

    def generate_interface_init(self, output_dir: Path):
        """Generate interface __init__.py"""
        handlers = [f.name for f in self.functions if not f.is_view]
        template = self.env.get_template('interface_init.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            handlers=[to_camel_case(h) + "Handler" for h in handlers]
        )
        output_path = self._append_template(output_dir / "__init__.py")
        self._write_formatted_python(content, output_path)

    def get_custom_implementations(self) -> List[Dict]:
        """Scan _custom folder for implementations"""
        custom_impls = []
        custom_dir = self.protocols_dir / "implementations" / "_custom"
        if custom_dir.exists():
            for file in custom_dir.glob("*.py"):
                if file.name == "__init__.py":
                    continue
                with open(file) as f:
                    content = f.read()
                    class_match = re.search(r"class (\w+)", content)
                    register_match = re.search(r"@register_implementation\(['\"](.+)['\"]\)", content)
                    if class_match and register_match:
                        custom_impls.append({
                            "folder": "_custom",
                            "file": file.stem,
                            "class_name": class_match.group(1),
                            "key": register_match.group(1)
                        })
        return custom_impls

    def generate_implementations(self, output_dir: Path):
        """Generate implementations"""
        # Individual implementation files
        for func in self.functions:
            if not func.is_view:
                template = self.env.get_template('implementation.py.j2')
                content = template.render(
                    contract_name=self.contract_name,
                    func=func
                )
                output_path = self._append_template(output_dir / f"{func.name}.py")
                self._write_formatted_python(content, output_path)

    def generate_main_implementations_init(self):
        """Generate main implementations/__init__.py"""
        template = self.env.get_template('implementations_main_init.py.j2')
        contracts_data = self._collect_contracts_data()
        custom_impls = self.get_custom_implementations()
        
        content = template.render(
            contracts=contracts_data,
            custom_implementations=custom_impls
        )
        output_path = self._append_template(self.protocols_dir / "implementations" / "__init__.py")
        self._write_formatted_python(content, output_path)

    def _collect_contracts_data(self) -> List[Dict]:
        """Collect contracts data and actual class names from implementations"""
        contracts_data = []
        implementations_dir = self.protocols_dir / "implementations"
        
        for contract_dir in implementations_dir.iterdir():
            if contract_dir.is_dir() and not contract_dir.name.startswith('_'):
                functions = []
                for impl_file in contract_dir.glob('*.py'):
                    if impl_file.name not in ['__init__.py', 'base.py', '__pycache__']:
                        try:
                            with open(impl_file) as f:
                                content = f.read()
                                # Extract actual class name from implementation file
                                class_match = re.search(r"class ([A-Za-z0-9]+)\(BaseImplementation\)", content)
                                if class_match:
                                    functions.append({
                                        'name': impl_file.stem.replace('_template', ''),
                                        'class_name': class_match.group(1),  # Use actual class name
                                        'key': f"{contract_dir.name}_{impl_file.stem}"
                                    })
                        except Exception as e:
                            logger.error(f"Failed to parse {impl_file}: {e}")

                if functions:
                    contracts_data.append({
                        'name': contract_dir.name,
                        'functions': functions
                    })
        return contracts_data

    def _write_formatted_python(self, content: str, path: Path):
        """Write formatted Python code"""
        try:
            formatted = black.format_str(content, mode=black.FileMode())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(formatted)
            logger.info(f"Generated {path}")
        except Exception as e:
            logger.error(f"Formatting failed for {path}: {e}")
            path.write_text(content)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("abi_path", help="Path to contract ABI JSON")
    parser.add_argument("--templates-dir", default="templates", help="Templates directory")
    args = parser.parse_args()
    
    generator = ContractGenerator(args.abi_path, args.templates_dir)
    generator.generate_all()