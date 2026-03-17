"""
PointCrypt Sender

Handles encryption of data on the sender side.
Combines formulas and blocks to create encrypted structure.
"""

from typing import List, Tuple, Dict
from core.utils import secure_hash, validate_seed, validate_block_count
from core.formulas import PointCryptFormulas
from core.blocks import BlockManager
import json


class PointCryptEncryptor:
    """
    Main encryptor class for sender side.
    
    Orchestrates the encryption process:
    1. Split data into blocks
    2. Generate sequence and points using formulas
    3. Shuffle blocks randomly based on seed
    4. Create mapping of points to original block positions
    5. Return shuffled blocks and encrypted structure
    """
    
    def __init__(self, seed: str, block_size: int = 4):
        """
        Initialize encryptor.
        
        Args:
            seed: Secret seed (shared with receiver)
            block_size: Size of each block (default 4 chars)
            
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
        
        # Track last encryption for reference
        self._last_block_count = None
        self._last_data_hash = None
    
    def encrypt(self, data: str) -> Dict:
        """
        Encrypt data using PointCrypt algorithm.
        
        Args:
            data: Data to encrypt (string)
            
        Returns:
            Dictionary with:
            - 'blocks': List of data blocks (shuffled order)
            - 'structure': Point-to-original-position mapping
            - 'block_count': Number of blocks
            - 'data_hash': Hash of original data
            - 'metadata': Additional info for debugging
            
        Example:
            >>> encryptor = PointCryptEncryptor(seed="my_secret")
            >>> result = encryptor.encrypt("HELLO WORLD")
            >>> 'blocks' in result
            True
        """
        if not isinstance(data, str) or len(data) == 0:
            raise ValueError("data must be non-empty string")
        
        # Step 1: Calculate data hash
        data_hash = secure_hash(data)
        self._last_data_hash = data_hash
        
        # Step 2: Split data into blocks (original order)
        original_blocks = self.block_manager.split_data(data)
        block_count = len(original_blocks)
        self._last_block_count = block_count
        
        if not validate_block_count(block_count):
            raise ValueError(f"Too many blocks ({block_count}). Max is 10000")
        
        # Step 3: Generate sequence and points using formulas
        formulas = PointCryptFormulas(
            seed=self.seed,
            block_count=block_count,
            data_hash=data_hash
        )
        sequence, points = formulas.generate_sequence_and_points()
        
        # Step 4: Create shuffled order with structure mapping
        shuffled_blocks, structure = self._shuffle_blocks_with_mapping(
            original_blocks, block_count
        )
        
        # Step 5: Convert structure to JSON
        structure_json = json.dumps(structure)
        
        return {
            'blocks': shuffled_blocks,
            'structure': structure_json,
            'block_count': block_count,
            'data_hash': data_hash,
            'metadata': {
                'sequence_sample': sequence[:3] if len(sequence) >= 3 else sequence,
                'points_sample': points[:3] if len(points) >= 3 else points,
                'block_size': self.block_size,
            }
        }
    
    def _shuffle_blocks_with_mapping(self, original_blocks: List[str], block_count: int) -> Tuple[List[str], Dict]:
        """
        Shuffle blocks deterministically and create mapping.
        
        Args:
            original_blocks: Blocks in original order
            block_count: Number of blocks
            
        Returns:
            Tuple of (shuffled_blocks, structure_mapping)
            
        The structure mapping is: point_index → original_block_position
        This tells receiver: "the block at point i originally came from position [value]"
        """
        import random
        
        # Seed the random generator for deterministic shuffling
        random.seed(self.seed)
        
        # Create indices for shuffling: [0, 1, 2, ...] → [shuffled]
        indices = list(range(block_count))
        random.shuffle(indices)
        
        # Shuffle blocks according to indices
        shuffled_blocks = [original_blocks[i] for i in indices]
        
        # Create structure mapping: point_index → where each shuffled block originally came from
        # shuffled_blocks[i] came from original position indices[i]
        structure = {}
        for i in range(block_count):
            point_key = f"point_{i}"
            structure[point_key] = indices[i]
        
        return shuffled_blocks, structure
    
    def get_encryption_info(self) -> Dict:
        """
        Get information about last encryption.
        
        Returns:
            Dictionary with encryption metadata
        """
        return {
            'seed': '***hidden***',
            'block_size': self.block_size,
            'last_block_count': self._last_block_count,
            'last_data_hash': self._last_data_hash,
        }
    
    def __repr__(self) -> str:
        return f"PointCryptEncryptor(seed=***hidden***, block_size={self.block_size})"


class EncryptionStructure:
    """
    Wrapper for encrypted structure.
    """
    
    def __init__(self, structure_json: str, block_count: int, data_hash: str):
        """
        Initialize encryption structure.
        
        Args:
            structure_json: JSON string of point→original_position mapping
            block_count: Number of blocks
            data_hash: Hash of original data
        """
        self.structure_json = structure_json
        self.block_count = block_count
        self.data_hash = data_hash
        self._structure_dict = None
    
    def get_structure_dict(self) -> Dict:
        """
        Parse JSON and return structure dictionary.
        
        Returns:
            Dictionary mapping point keys to original block positions
        """
        if self._structure_dict is None:
            self._structure_dict = json.loads(self.structure_json)
        return self._structure_dict
    
    def get_size_bytes(self) -> int:
        """
        Get size of structure in bytes.
        
        Returns:
            Size in bytes
        """
        return len(self.structure_json.encode('utf-8'))
    
    def __repr__(self) -> str:
        return f"EncryptionStructure(blocks={self.block_count}, size={self.get_size_bytes()} bytes)"


class EncryptionResult:
    """
    Complete encryption result combining all components.
    """
    
    def __init__(self, blocks: List[str], structure: str, 
                 block_count: int, data_hash: str, metadata: Dict = None):
        """
        Initialize encryption result.
        
        Args:
            blocks: List of data blocks (shuffled)
            structure: Point-to-original-position mapping (JSON)
            block_count: Number of blocks
            data_hash: Hash of original data
            metadata: Optional metadata dictionary
        """
        self.blocks = blocks
        self.structure = structure
        self.block_count = block_count
        self.data_hash = data_hash
        self.metadata = metadata or {}
    
    def get_total_size(self) -> Dict:
        """
        Calculate total data size for transmission.
        
        Returns:
            Dictionary with size breakdown
        """
        blocks_size = sum(len(b.encode('utf-8')) for b in self.blocks)
        structure_size = len(self.structure.encode('utf-8'))
        
        return {
            'blocks_size_bytes': blocks_size,
            'structure_size_bytes': structure_size,
            'total_bytes': blocks_size + structure_size,
            'block_count': self.block_count,
            'data_hash': self.data_hash,
        }
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            'blocks': self.blocks,
            'structure': self.structure,
            'block_count': self.block_count,
            'data_hash': self.data_hash,
            'metadata': self.metadata,
        }
    
    def __repr__(self) -> str:
        size_info = self.get_total_size()
        return (
            f"EncryptionResult("
            f"blocks={size_info['block_count']}, "
            f"size={size_info['total_bytes']} bytes"
            f")"
        )


if __name__ == "__main__":
    # Quick test of encryption
    print("🧪 Testing PointCrypt Encryptor\n")
    
    print("Test 1: Basic Encryption")
    encryptor = PointCryptEncryptor(seed="test_secret", block_size=4)
    result = encryptor.encrypt("HELLO WORLD")
    print(f"  Original data: 'HELLO WORLD'")
    print(f"  Shuffled blocks: {result['blocks']}")
    print(f"  Block count: {result['block_count']}")
    print(f"  Data hash: {result['data_hash'][:16]}...")
    
    print("\nTest 2: Encryption Structure")
    enc_structure = EncryptionStructure(
        result['structure'],
        result['block_count'],
        result['data_hash']
    )
    print(f"  Structure size: {enc_structure.get_size_bytes()} bytes")
    structure_dict = enc_structure.get_structure_dict()
    print(f"  Structure entries: {len(structure_dict)}")
    for key, val in list(structure_dict.items())[:3]:
        print(f"    {key} → {val}")
    
    print("\nTest 3: Encryption Result")
    enc_result = EncryptionResult(
        result['blocks'],
        result['structure'],
        result['block_count'],
        result['data_hash'],
        result['metadata']
    )
    size_info = enc_result.get_total_size()
    print(f"  Blocks size: {size_info['blocks_size_bytes']} bytes")
    print(f"  Structure size: {size_info['structure_size_bytes']} bytes")
    print(f"  Total size: {size_info['total_bytes']} bytes")
    
    print("\nTest 4: Encryption Info")
    info = encryptor.get_encryption_info()
    print(f"  Encryption info: {info}")
    
    print("\nTest 5: Large Data")
    large_data = "A" * 1000
    result2 = encryptor.encrypt(large_data)
    enc_result2 = EncryptionResult(
        result2['blocks'],
        result2['structure'],
        result2['block_count'],
        result2['data_hash']
    )
    size_info2 = enc_result2.get_total_size()
    print(f"  Data size: 1000 characters")
    print(f"  Block count: {size_info2['block_count']}")
    print(f"  Total encrypted size: {size_info2['total_bytes']} bytes")
    
    print("\n✅ All encryptor tests passed!")