from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os
import re
from jinja2 import Environment, FileSystemLoader
import logging
import black
import json
import argparse

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
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name in self.PYTHON_KEYWORDS:
                param_name = f"{param_name}_"
            if param_name == 'sender':
                param_name = 'sender_account'
            elif param_name == 'value':
                param_name = 'value_amount'
            params.append(param_name)
        return ", ".join(params)

    def get_python_param_defs(self) -> str:
        params = []
        for i, inp in enumerate(self.inputs):
            param_name = inp['name'] if inp['name'] else f"param{i}"
            if param_name in self.PYTHON_KEYWORDS:
                param_name = f"{param_name}_"
            if param_name == 'sender':
                param_name = 'sender_account'
            elif param_name == 'value':
                param_name = 'value_amount'
            param_type = self._get_python_type(inp['type'])
            params.append(f"{param_name}: {param_type}")
        return ", ".join(params)

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

class GenericContractGenerator:
    def __init__(self, abi_path: str, templates_dir: str = "templates", project_root: Path = None):
        self.abi_path = Path(abi_path)
        name = self.abi_path.stem
        if name.startswith('0x'):
            parent_dir = self.abi_path.parent.name
            self.contract_name = to_camel_case(parent_dir)
        else:
            self.contract_name = name

        self.project_root = project_root or Path(__file__).parents[2]
        self.protocols_dir = self.project_root / "src" / "protocols"
        
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        with open(abi_path) as f:
            self.abi = json.load(f)
            
        self.functions = []
        self._parse_abi()

    def _parse_abi(self):
        for entry in self.abi:
            if entry['type'] == 'function':
                self.functions.append(ContractFunction(entry))

    def generate_all(self):
        output_dir = self.protocols_dir / "interfaces" / self.contract_name.lower()
        output_dir.mkdir(parents=True, exist_ok=True)

        self.generate_client(output_dir)
        self.generate_handler(output_dir)  
        self.generate_init(output_dir)

    def generate_client(self, output_dir: str):
        template = self.env.get_template('generic_client.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            functions=self.functions
        )
        output_path = Path(output_dir) / f"{self.contract_name.lower()}_client_template.py"
        self._write_formatted_python(content, output_path)

    def generate_handler(self, output_dir: str):
        action_functions = [f for f in self.functions if not f.is_view]
        template = self.env.get_template('generic_handler.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            functions=action_functions
        )
        output_path = Path(output_dir) / f"{self.contract_name.lower()}_handler_template.py"
        self._write_formatted_python(content, output_path)

    def generate_init(self, output_dir: str):
        """Generate __init__.py with proper handler names"""
        action_functions = [f for f in self.functions if not f.is_view]
        template = self.env.get_template('generic_init.py.j2')
        content = template.render(
            contract_name=self.contract_name,
            handlers=action_functions 
        )
        output_path = Path(output_dir) / "__init___template.py"
        self._write_formatted_python(content, output_path)

    def _write_formatted_python(self, content: str, path: Path):
        try:
            formatted = black.format_str(content, mode=black.FileMode())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(formatted)
            logger.info(f"Generated {path}")
        except Exception as e:
            logger.error(f"Formatting failed for {path}: {e}")
            path.write_text(content)

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
        return ''.join(words)
    else:
        return ''.join(word.capitalize() for word in name.split('_'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("abi_path", help="Path to contract ABI JSON")
    parser.add_argument("--templates-dir", default=Path(__file__).parent / "templates", help="Templates directory")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    args = parser.parse_args()
    
    generator = GenericContractGenerator(
        args.abi_path, 
        args.templates_dir,
        args.project_root
    )
    generator.generate_all()