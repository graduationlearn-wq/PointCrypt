"""
PointCrypt Receiver

Handles decryption of data on the receiver side.
Reconstructs formulas and recovers original data from encrypted structure.
"""

from typing import List, Tuple, Dict
import json
from core.utils import secure_hash, validate_seed, validate_block_count
from core.formulas import PointCryptFormulas
from core.blocks import BlockManager


class PointCryptDecryptor:
    """
    Main decryptor class for receiver side.
    
    Orchestrates the decryption process:
    1. Receive shuffled blocks and encrypted structure
    2. Decrypt structure using seed
    3. Use structure to unscramble blocks back to original order
    4. Reassemble blocks into original data
    """
    
    def __init__(self, seed: str, block_size: int = 4):
        """
        Initialize decryptor.
        
        Args:
            seed: Secret seed (same as sender)
            block_size: Size of each block (same as sender, default 4 chars)
            
        Raises:
            ValueError: If seed is invalid
        """
        if not validate_seed(seed):
            raise ValueError("Invalid seed: must be non-empty and <= 10000 chars")
        
        if not isinstance(block_size, int) or block_size <= 0:
            raise ValueError("block_size must be positive integer")
        
        self.seed = seed
        self.block_size = block_size
        self.block_manager = BlockManager(block_size)
        
        # Track last decryption for reference
        self._last_block_count = None
        self._last_data_hash = None
        self._recovered_data = None
        self._debug_info = {}
    
    def decrypt(self, encrypted_data: Dict, debug: bool = False) -> str:
        """
        Decrypt data using PointCrypt algorithm.
        
        Args:
            encrypted_data: Dictionary with:
            - 'blocks': List of shuffled data blocks
            - 'structure': Point-to-original-position mapping (JSON string)
            - 'block_count': Number of blocks
            - 'data_hash': Hash of original data
            debug: If True, print debug information
            
        Returns:
            Decrypted original data (string)
        """
        # Step 1: Validate and extract inputs
        if not isinstance(encrypted_data, dict):
            raise TypeError("encrypted_data must be a dictionary")
        
        required_keys = ['blocks', 'structure', 'block_count', 'data_hash']
        for key in required_keys:
            if key not in encrypted_data:
                raise KeyError(f"Missing required key: {key}")
        
        shuffled_blocks = encrypted_data['blocks']
        structure_json = encrypted_data['structure']
        block_count = encrypted_data['block_count']
        data_hash = encrypted_data['data_hash']
        
        # Store for reference
        self._last_block_count = block_count
        self._last_data_hash = data_hash
        
        # Step 2: Validate block count
        if not validate_block_count(block_count):
            raise ValueError(f"Invalid block_count: {block_count}")
        
        if len(shuffled_blocks) != block_count:
            raise ValueError(
                f"Block count mismatch: expected {block_count}, got {len(shuffled_blocks)}"
            )
        
        # Step 3: Parse structure
        try:
            structure_dict = json.loads(structure_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse structure JSON: {e}")
        
        if debug:
            print("\n=== DECRYPTION DEBUG INFO ===")
            print(f"Shuffled blocks received: {shuffled_blocks}")
            print(f"Structure mapping:")
            for key, val in list(structure_dict.items())[:3]:
                print(f"  {key} → {val}")
        
        # Step 4: RECOVER BLOCKS IN ORIGINAL ORDER
        # The structure tells us: shuffled_blocks[i] originally came from position structure['point_i']
        # We need to put each shuffled block back to its original position
        
        original_order_blocks = [None] * block_count
        
        for i in range(block_count):
            point_key = f"point_{i}"
            
            if point_key not in structure_dict:
                raise KeyError(f"Point key {point_key} not found in structure")
            
            # Get the original position of this block
            original_position = structure_dict[point_key]
            
            if not isinstance(original_position, int) or original_position < 0 or original_position >= block_count:
                raise ValueError(f"Invalid block position: {original_position}")
            
            # shuffled_blocks[i] belongs at original_position
            original_order_blocks[original_position] = shuffled_blocks[i]
            
            if debug and i < 3:
                print(f"  shuffled_blocks[{i}]='{shuffled_blocks[i]}' → original position {original_position}")
        
        if debug:
            print(f"Reconstructed order: {original_order_blocks}")
        
        # Step 5: Reassemble blocks into original data
        recovered_data = self.block_manager.reassemble_data(original_order_blocks)
        self._recovered_data = recovered_data
        
        return recovered_data
    
    def get_debug_info(self) -> Dict:
        """
        Get debug information from last decryption.
        
        Returns:
            Dictionary with debug data
        """
        return self._debug_info
    
    def verify_decryption(self, original_data: str) -> bool:
        """
        Verify that decrypted data matches original.
        
        Args:
            original_data: Original data before encryption
            
        Returns:
            True if decryption is correct, False otherwise
        """
        if self._recovered_data is None:
            raise RuntimeError("No data decrypted yet. Call decrypt() first")
        return self._recovered_data == original_data
    
    def get_decryption_info(self) -> Dict:
        """
        Get information about last decryption.
        
        Returns:
            Dictionary with decryption metadata
        """
        return {
            'seed': '***hidden***',
            'block_size': self.block_size,
            'last_block_count': self._last_block_count,
            'last_data_hash': self._last_data_hash,
            'recovered_data_available': self._recovered_data is not None,
        }
    
    def __repr__(self) -> str:
        return f"PointCryptDecryptor(seed=***hidden***, block_size={self.block_size})"


class DecryptionResult:
    """
    Wrapper for decryption result with metadata.
    """
    
    def __init__(self, decrypted_data: str, block_count: int, 
                 data_hash: str, original_data: str = None):
        """
        Initialize decryption result.
        
        Args:
            decrypted_data: The decrypted data
            block_count: Number of blocks
            data_hash: Hash of original data
            original_data: Optional original data for verification
        """
        self.decrypted_data = decrypted_data
        self.block_count = block_count
        self.data_hash = data_hash
        self.original_data = original_data
    
    def is_verified(self) -> bool:
        """
        Check if decryption was successful (data matches original if provided).
        
        Returns:
            True if verified, False if not, None if no original data provided
        """
        if self.original_data is None:
            return None
        return self.decrypted_data == self.original_data
    
    def get_verification_status(self) -> str:
        """
        Get human-readable verification status.
        
        Returns:
            Status string
        """
        if self.original_data is None:
            return "UNVERIFIED (no original data provided)"
        elif self.is_verified():
            return "✅ VERIFIED (matches original)"
        else:
            return "❌ FAILED (does not match original)"
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            'decrypted_data': self.decrypted_data,
            'block_count': self.block_count,
            'data_hash': self.data_hash,
            'verification_status': self.get_verification_status(),
        }
    
    def __repr__(self) -> str:
        status = self.get_verification_status()
        return f"DecryptionResult(blocks={self.block_count}, status={status})"


class EndToEndTest:
    """
    Helper class to test encryption and decryption together.
    """
    
    def __init__(self, seed: str, block_size: int = 4):
        """
        Initialize end-to-end test.
        
        Args:
            seed: Shared secret seed
            block_size: Block size
        """
        self.seed = seed
        self.block_size = block_size
    
    def test_roundtrip(self, original_data: str, debug: bool = False) -> Tuple[bool, str]:
        """
        Test encryption then decryption roundtrip.
        
        Args:
            original_data: Data to encrypt and decrypt
            debug: If True, print debug information
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        from sender.encryptor import PointCryptEncryptor
        
        try:
            # Encrypt
            encryptor = PointCryptEncryptor(self.seed, self.block_size)
            encrypted = encryptor.encrypt(original_data)
            
            # Decrypt
            decryptor = PointCryptDecryptor(self.seed, self.block_size)
            decrypted = decryptor.decrypt(encrypted, debug=debug)
            
            # Verify
            success = decrypted == original_data
            
            if success:
                message = f"✅ Roundtrip successful: '{original_data}' → encrypted → '{decrypted}'"
            else:
                message = (
                    f"❌ Roundtrip failed:\n"
                    f"  Original:  '{original_data}'\n"
                    f"  Decrypted: '{decrypted}'"
                )
            
            return success, message
        
        except Exception as e:
            return False, f"❌ Roundtrip error: {e}"


if __name__ == "__main__":
    # Quick test of decryption with debug
    print("🧪 Testing PointCrypt Decryptor\n")
    
    from sender.encryptor import PointCryptEncryptor
    
    print("Test 1: Encrypt then Decrypt (WITH DEBUG)")
    seed = "test_secret_key"
    original_data = "HELLO WORLD"
    
    # Encrypt
    encryptor = PointCryptEncryptor(seed=seed, block_size=4)
    encrypted = encryptor.encrypt(original_data)
    print(f"  Original: '{original_data}'")
    print(f"  Encrypted blocks: {encrypted['blocks']}")
    
    # Decrypt with debug
    decryptor = PointCryptDecryptor(seed=seed, block_size=4)
    decrypted = decryptor.decrypt(encrypted, debug=True)
    print(f"  Decrypted: '{decrypted}'")
    print(f"  Match: {decrypted == original_data}")
    
    print("\nTest 2: Decryption Result")
    result = DecryptionResult(
        decrypted,
        encrypted['block_count'],
        encrypted['data_hash'],
        original_data
    )
    print(f"  Verification: {result.get_verification_status()}")
    print(f"  Result: {result}")
    
    print("\nTest 3: End-to-End Roundtrip Tests")
    e2e = EndToEndTest(seed=seed, block_size=4)
    
    test_cases = [
        "HELLO WORLD",
        "TEST DATA",
        "A",
        "ABCDEFGHIJKLMNOP",
        "The quick brown fox jumps over the lazy dog"
    ]
    
    all_passed = True
    for test_data in test_cases:
        success, message = e2e.test_roundtrip(test_data, debug=False)
        print(f"  {message}")
        if not success:
            all_passed = False
    
    print("\nTest 4: Decryption Info")
    info = decryptor.get_decryption_info()
    print(f"  Decryption info: {info}")
    
    if all_passed:
        print("\n✅ All decryptor tests passed!")
    else:
        print("\n❌ Some tests failed!")