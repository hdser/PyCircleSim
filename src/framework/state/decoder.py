from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from eth_typing import HexStr
from eth_utils import keccak, to_checksum_address
from ape import chain, Contract
from src.framework.logging import get_logger


logger = get_logger(__name__)

@dataclass 
class StateVariable:
    """Configuration for a state variable to decode"""
    name: str
    type: str
    slot: int
    iterable: bool = False  # If this is a mapping that should be iterated


class StateDecoder:
    """Decodes Ethereum contract state variables"""
    
    def __init__(self, contract_address: str):
        self.contract_address = contract_address

    def decode_state(self, variables: Dict[str, Dict[str, Any]], block_identifier: Optional[int] = None) -> Dict[str, Any]:
        """
        Decode state variables based on config
        
        Args:
            variables: Dict of variable configs from network_config['state_variables']
            block_identifier: Optional block number to read state from
            
        Returns:
            Dict of decoded values
        """
        result = {}
        for name, settings in variables.items():
            try:
                var = StateVariable(
                    name=name,
                    type=settings['type'],
                    slot=settings['slot'],
                    iterable=settings.get('iterable', False)
                )
                value = self._decode_variable(var, block_identifier)
                result[name] = value
            except Exception as e:
                logger.error(f"Error decoding {name}: {e}")
                result[name] = None
        return result

    def _decode_variable(self, var: StateVariable, block_identifier: Optional[int] = None) -> Any:
        """Decode a single variable based on its type"""
        if var.iterable:
            return self._decode_iterable_mapping(var, block_identifier)
            
        if var.type == 'uint256':
            return self._decode_uint256(var.slot, block_identifier)
        elif var.type == 'address':
            return self._decode_address(var.slot, block_identifier)
        elif var.type.startswith('int128['):
            length = int(var.type[7:-1])  # Extract array length
            return self._decode_int128_array(var.slot, length, block_identifier)
        elif var.type == 'string':
            return self._decode_string(var.slot, block_identifier)
        elif var.type == 'bool':
            return self._decode_bool(var.slot, block_identifier)
        elif var.type == 'bytes32':
            return self._decode_bytes32(var.slot, block_identifier)
        else:
            raise ValueError(f"Unsupported type: {var.type}")

    def _read_slot(self, slot: int, block_identifier: Optional[int] = None) -> bytes:
        """Read a storage slot from the contract"""
        return chain.provider.get_storage(self.contract_address, slot, block_identifier)

    def _decode_uint256(self, slot: int, block_identifier: Optional[int] = None) -> int:
        """Decode a uint256 from storage"""
        value = self._read_slot(slot, block_identifier)
        return int.from_bytes(value, byteorder='big')

    def _decode_address(self, slot: int, block_identifier: Optional[int] = None) -> str:
        """Decode an address from storage"""
        value = self._read_slot(slot, block_identifier)
        return to_checksum_address(value[-20:].hex())

    def _decode_int128_array(self, slot_start: int, length: int, block_identifier: Optional[int] = None) -> List[int]:
        """Decode a static array of int128"""
        elements = []
        num_slots = (length + 1) // 2
        
        for i in range(num_slots):
            slot_index = slot_start + i
            word = self._read_slot(slot_index, block_identifier)
            
            # Each slot contains two int128 values
            first_half = word[0:16]
            second_half = word[16:32]
            
            # Decode first value
            elements.append(int.from_bytes(first_half, byteorder='big', signed=True))
            
            # Add second value if we haven't reached the end
            if len(elements) < length:
                elements.append(int.from_bytes(second_half, byteorder='big', signed=True))
                
        return elements

    def _decode_string(self, slot: int, block_identifier: Optional[int] = None) -> str:
        """Decode a string from storage"""
        main_slot = self._read_slot(slot, block_identifier)
        length_full = int.from_bytes(main_slot, byteorder='big')
        short_string_flag = (length_full & 1) == 1
        
        if short_string_flag:
            length = length_full >> 1
            raw_bytes = main_slot[0:length]
            return raw_bytes.decode("utf-8", errors="replace")
        else:
            # Long string case
            if length_full == 0:
                return ""
            
            slot_bytes = slot.to_bytes(32, byteorder='big')
            content_slot = keccak(slot_bytes)
            content_slot_index = int.from_bytes(content_slot, byteorder='big')
            content = self._read_slot(content_slot_index, block_identifier)
            
            return content.decode("utf-8", errors="replace").rstrip('\x00')

    def _decode_iterable_mapping(self, var: StateVariable, block_identifier: Optional[int] = None) -> List[Any]:
        """
        Decode an iterable mapping (like the avatars linked list)
        Currently only supports the avatar pattern seen in the Circles contract
        """
        if var.name != 'avatars':
            raise ValueError("Only avatars mapping iteration is currently supported")
            
        # Constants from the Circles contract
        SENTINEL = "0x0000000000000000000000000000000000000001"
        results = []
        
        # Start from sentinel
        current = SENTINEL
        while True:
            next_addr = self._read_mapping(var.slot, current, block_identifier)
            if next_addr == SENTINEL:
                break
                
            results.append(next_addr)
            current = next_addr
            
        return results
        
    def _read_mapping(self, mapping_slot: int, key: str, block_identifier: Optional[int] = None) -> str:
        """Read a value from a mapping given its slot and key"""
        key_bytes = bytes.fromhex(key[2:].rjust(40, '0'))
        key_padded = key_bytes.rjust(32, b'\x00')
        slot_padded = mapping_slot.to_bytes(32, byteorder='big')
        
        location = keccak(key_padded + slot_padded)
        value = self._read_slot(int.from_bytes(location, 'big'), block_identifier)
        
        # For addresses, return the last 20 bytes
        return to_checksum_address(value[-20:].hex())