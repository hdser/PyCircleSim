from typing import Any, Dict, List, Optional, Union, NamedTuple, Tuple
from dataclasses import dataclass
from eth_typing import HexStr
from eth_utils import keccak, to_checksum_address
from ape import chain, Contract
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__)

class TrustMarker(NamedTuple):
    """Structure for trust marker data"""
    previous: str  # address
    expiry: int    # uint96

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
        # Constants
        self.SENTINEL = "0x0000000000000000000000000000000000000001"
        self.ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

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
                logger.info(f"Decoding {var}")
                value = self._decode_variable(var, block_identifier)
                result[name] = value
            except Exception as e:
                logger.error(f"Error decoding {name}: {e}")
                result[name] = None
        return result

    def _decode_variable(self, var: StateVariable, block_identifier: Optional[int] = None) -> Any:
        """Decode a single variable based on its type"""
        if var.iterable:
            if var.name == 'avatars':
                return self._decode_avatar_mapping(var, block_identifier)
            elif var.name == 'trustMarkers':
                return self._decode_trust_markers_mapping(var, block_identifier)
            else:
                raise ValueError(f"Mapping {var.name} iteration not supported")
            
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

    def _decode_avatar_mapping(self, var: StateVariable, block_identifier: Optional[int] = None) -> List[str]:
        """Decode the avatars linked list mapping"""
        results = []
        current = self.SENTINEL

        while True:
            next_addr = self._read_mapping(var.slot, current, block_identifier)
            if next_addr == self.SENTINEL:
                break
            results.append(next_addr)
            current = next_addr
            
        return results


    def _decode_trust_markers_mapping(
        self,
        var: StateVariable, 
        block_identifier: Optional[int] = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Decode the trust markers double mapping into a dictionary-of-dictionaries:
            {
            <truster_address>: {
                <trustee_address>: <expiry_int>,
                ...
            },
            ...
            }

        We ignore the 'previous' field from the on-chain struct and only store `expiry`.
        """
        results: Dict[str, Dict[str, int]] = {}

        # Decode the avatars list first so we know which "trusters" to iterate
        avatars = self._decode_avatar_mapping(
            StateVariable(name='avatars', type='mapping(address => address)', slot=26, iterable=True),
            block_identifier
        )
        # We also append the SENTINEL so the iteration code below matches your existing pattern:
        avatars.append(self.SENTINEL)

        for truster in avatars:
            # 1) Read the sentinel marker for this truster
            sentinel_marker = self._read_trust_marker(var.slot, truster, self.SENTINEL, block_identifier)

            # If the sentinel marker has zero_address as "previous", that means no trust list
            if sentinel_marker.previous == self.ZERO_ADDRESS:
                continue

            # 2) Follow the linked list starting from sentinel_marker.previous
            current = sentinel_marker.previous
            visited = set()

            while current != self.SENTINEL and current not in visited:
                visited.add(current)
                current_marker = self._read_trust_marker(var.slot, truster, current, block_identifier)
                
                # If expiry > 0, record it
                if current_marker.expiry > 0:
                    if truster not in results:
                        results[truster] = {}
                    # Store trustee => expiry
                    results[truster][current] = current_marker.expiry

                # Move to the next in the linked list
                current = current_marker.previous

        return results


    def _read_trust_marker(self, base_slot: int, truster: str, trustee: str, block_identifier: Optional[int] = None) -> TrustMarker:
        """
        Read a TrustMarker struct from storage using the correct struct layout:
          struct TrustMarker {
              address previous; // lower 160 bits, i.e. rightmost 20 bytes
              uint96  expiry;   // upper 96 bits, i.e. leftmost 12 bytes
          }
        """
        # Calculate storage slot
        truster_bytes = bytes.fromhex(truster[2:].rjust(40, '0'))
        truster_padded = truster_bytes.rjust(32, b'\x00')
        slot_padded = base_slot.to_bytes(32, byteorder='big')
        
        intermediate_hash = keccak(truster_padded + slot_padded)
        
        trustee_bytes = bytes.fromhex(trustee[2:].rjust(40, '0'))
        trustee_padded = trustee_bytes.rjust(32, b'\x00')
        
        final_hash = keccak(trustee_padded + intermediate_hash)
        location = int.from_bytes(final_hash, byteorder='big')
        
        # Read storage slot
        data = self._read_slot(location, block_identifier)
        
        # Parse TrustMarker struct:
        # The first 12 bytes => expiry (uint96, stored in upper bits)
        # The last 20 bytes => previous address
        expiry = int.from_bytes(data[:12], byteorder='big')
        previous = to_checksum_address(data[12:].hex())
        
        logger.debug(f"Storage slot for {truster}->{trustee}:")
        logger.debug(f"  Location: {hex(location)}")
        logger.debug(f"  Raw data: {data.hex()}")
        logger.debug(f"  Parsed:")
        logger.debug(f"    Previous: {previous}")
        logger.debug(f"    Expiry: {expiry}")
        
        return TrustMarker(previous=previous, expiry=expiry)

    def _get_double_mapping_location(self, base_slot: int, truster: str, trustee: str) -> int:
        """
        Helper to compute the double mapping's final storage slot:
          trustMarkers[truster][trustee]
        """
        truster_bytes = bytes.fromhex(truster[2:].rjust(40, '0')).rjust(32, b'\x00')
        base_slot_bytes = base_slot.to_bytes(32, byteorder='big')
        intermediate_hash = keccak(truster_bytes + base_slot_bytes)
        
        trustee_bytes = bytes.fromhex(trustee[2:].rjust(40, '0')).rjust(32, b'\x00')
        final_hash = keccak(trustee_bytes + intermediate_hash)
        return int.from_bytes(final_hash, byteorder='big')

    # Keep existing methods unchanged below

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

    def _decode_bool(self, slot: int, block_identifier: Optional[int] = None) -> bool:
        """Decode a bool from storage"""
        data = self._read_slot(slot, block_identifier)
        return bool(int.from_bytes(data, byteorder='big'))

    def _decode_bytes32(self, slot: int, block_identifier: Optional[int] = None) -> HexStr:
        """Decode a bytes32 from storage"""
        data = self._read_slot(slot, block_identifier)
        return HexStr(data.hex())

    def _read_mapping(self, mapping_slot: int, key: str, block_identifier: Optional[int] = None) -> str:
        """Read a value from a mapping given its slot and key"""
        key_bytes = bytes.fromhex(key[2:].rjust(40, '0'))
        key_padded = key_bytes.rjust(32, b'\x00')
        slot_padded = mapping_slot.to_bytes(32, byteorder='big')
        
        location = keccak(key_padded + slot_padded)
        value = self._read_slot(int.from_bytes(location, 'big'), block_identifier)
        
        # For addresses, return the last 20 bytes
        return to_checksum_address(value[-20:].hex())
