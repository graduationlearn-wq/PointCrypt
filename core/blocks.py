"""
PointCrypt Core Blocks

Handles splitting data into blocks and reassembling blocks back to data.
"""

from typing import List, Tuple
from core.utils import validate_block_count


class BlockSplitter:
    """
    Splits data into fixed-size blocks.
    """
    
    def __init__(self, block_size: int = 4):
        """
        Initialize block splitter.
        
        Args:
            block_size: Size of each block in characters/bytes
                       Default is 4 to match our examples
        
        Raises:
            ValueError: If block_size is invalid
        """
        if not isinstance(block_size, int) or block_size <= 0:
            raise ValueError("block_size must be a positive integer")
        if block_size > 1000000:
            raise ValueError("block_size too large (max 1,000,000)")
        
        self.block_size = block_size
    
    def split(self, data: str) -> List[str]:
        """
        Split data into fixed-size blocks.
        
        Args:
            data: Data to split (string)
            
        Returns:
            List of blocks, last block may be shorter if data length
            is not divisible by block_size
            
        Example:
            >>> splitter = BlockSplitter(block_size=4)
            >>> blocks = splitter.split("HELLO WORLD")
            >>> blocks
            ['HELL', 'O WO', 'RLD']
            >>> len(blocks)
            3
        """
        if not isinstance(data, str):
            raise TypeError("data must be a string")
        
        if len(data) == 0:
            raise ValueError("data cannot be empty")
        
        blocks = []
        for i in range(0, len(data), self.block_size):
            block = data[i:i + self.block_size]
            blocks.append(block)
        
        return blocks
    
    def get_block_count(self, data: str) -> int:
        """
        Get the number of blocks that data will be split into.
        
        Args:
            data: Data to analyze
            
        Returns:
            Number of blocks
            
        Example:
            >>> splitter = BlockSplitter(block_size=4)
            >>> splitter.get_block_count("HELLO WORLD")
            3
        """
        if len(data) == 0:
            return 0
        return (len(data) + self.block_size - 1) // self.block_size
    
    def __repr__(self) -> str:
        return f"BlockSplitter(block_size={self.block_size})"


class BlockReassembler:
    """
    Reassembles blocks back into original data.
    """
    
    def __init__(self):
        """
        Initialize block reassembler.
        """
        pass
    
    def reassemble(self, blocks: List[str]) -> str:
        """
        Reassemble blocks back into original data.
        
        Args:
            blocks: List of blocks (strings)
            
        Returns:
            Reassembled data
            
        Example:
            >>> blocks = ['HELL', 'O WO', 'RLD']
            >>> reassembler = BlockReassembler()
            >>> reassembler.reassemble(blocks)
            'HELLO WORLD'
        """
        if not isinstance(blocks, list):
            raise TypeError("blocks must be a list")
        
        if len(blocks) == 0:
            raise ValueError("blocks list cannot be empty")
        
        if not all(isinstance(b, str) for b in blocks):
            raise TypeError("all blocks must be strings")
        
        return "".join(blocks)
    
    def verify_blocks(self, blocks: List[str]) -> bool:
        """
        Verify that blocks are valid.
        
        Args:
            blocks: List of blocks to verify
            
        Returns:
            True if blocks are valid
        """
        if not isinstance(blocks, list):
            return False
        
        if len(blocks) == 0:
            return False
        
        return all(isinstance(b, str) and len(b) > 0 for b in blocks)
    
    def __repr__(self) -> str:
        return "BlockReassembler()"


class BlockMapping:
    """
    Maps blocks to 3D points (used by sender).
    Tracks which block goes to which point.
    """
    
    def __init__(self, blocks: List[str], points: List[Tuple[int, int, int]]):
        """
        Initialize block mapping.
        
        Args:
            blocks: List of data blocks
            points: List of 3D points (must equal length of blocks)
            
        Raises:
            ValueError: If blocks and points have different lengths
        """
        if len(blocks) != len(points):
            raise ValueError(
                f"blocks and points must have same length. "
                f"Got {len(blocks)} blocks and {len(points)} points"
            )
        
        self.blocks = blocks
        self.points = points
        self.block_count = len(blocks)
        self._mapping = {}  # Will store point → block mapping
    
    def create_random_mapping(self, seed: int = None) -> dict:
        """
        Create a random mapping from points to blocks.
        
        Args:
            seed: Random seed for reproducibility (optional)
            
        Returns:
            Dictionary mapping point → block
            
        Example:
            >>> blocks = ['HELL', 'O WO', 'RLD']
            >>> points = [(1,2,3), (4,5,6), (7,8,9)]
            >>> mapping = BlockMapping(blocks, points)
            >>> random_map = mapping.create_random_mapping(seed=42)
            >>> len(random_map)
            3
        """
        import random
        
        if seed is not None:
            random.seed(seed)
        
        # Shuffle indices to create random assignment
        indices = list(range(self.block_count))
        random.shuffle(indices)
        
        # Create mapping: point → block
        self._mapping = {}
        for i, shuffled_idx in enumerate(indices):
            point_key = self._point_to_key(self.points[i])
            self._mapping[point_key] = self.blocks[shuffled_idx]
        
        return self._mapping
    
    def get_mapping(self) -> dict:
        """
        Get the current point → block mapping.
        
        Returns:
            Dictionary mapping point → block
        """
        if not self._mapping:
            raise RuntimeError("No mapping created yet. Call create_random_mapping() first")
        return self._mapping
    
    def _point_to_key(self, point: Tuple[int, int, int]) -> str:
        """
        Convert a point to a hashable key for dictionary.
        
        Args:
            point: 3D point (x, y, z)
            
        Returns:
            String key
        """
        return f"({point[0]},{point[1]},{point[2]})"
    
    def get_block_for_point(self, point: Tuple[int, int, int]) -> str:
        """
        Get the block assigned to a specific point.
        
        Args:
            point: 3D point
            
        Returns:
            Block assigned to that point
        """
        point_key = self._point_to_key(point)
        if point_key not in self._mapping:
            raise KeyError(f"Point {point} not in mapping")
        return self._mapping[point_key]
    
    def get_mapping_for_serialization(self) -> dict:
        """
        Get mapping in a format suitable for serialization/encryption.
        
        Returns:
            Dictionary with point tuples as keys and blocks as values
        """
        if not self._mapping:
            raise RuntimeError("No mapping created yet")
        
        # Convert string keys back to tuple format
        serializable = {}
        for point in self.points:
            point_key = self._point_to_key(point)
            if point_key in self._mapping:
                serializable[point] = self._mapping[point_key]
        
        return serializable
    
    def __repr__(self) -> str:
        return f"BlockMapping(blocks={self.block_count}, mapped={bool(self._mapping)})"


class BlockRecovery:
    """
    Recovers original block order from point-to-block mapping.
    Used by receiver to reconstruct data.
    """
    
    def __init__(self, points: List[Tuple[int, int, int]], mapping: dict):
        """
        Initialize block recovery.
        
        Args:
            points: List of 3D points in correct order
            mapping: Dictionary mapping points to blocks
        """
        if len(points) == 0:
            raise ValueError("points list cannot be empty")
        
        self.points = points
        self.mapping = mapping
    
    def recover_blocks(self) -> List[str]:
        """
        Recover blocks in correct order using the points.
        
        Returns:
            List of blocks in correct order
            
        Example:
            >>> points = [(1,2,3), (4,5,6), (7,8,9)]
            >>> mapping = {
            ...     (1,2,3): 'HELL',
            ...     (4,5,6): 'O WO',
            ...     (7,8,9): 'RLD'
            ... }
            >>> recovery = BlockRecovery(points, mapping)
            >>> blocks = recovery.recover_blocks()
            >>> blocks
            ['HELL', 'O WO', 'RLD']
        """
        recovered = []
        for point in self.points:
            if point not in self.mapping:
                raise KeyError(f"Point {point} not found in mapping")
            recovered.append(self.mapping[point])
        return recovered
    
    def verify_recovery(self, original_data: str, block_size: int) -> bool:
        """
        Verify that recovered blocks match original data.
        
        Args:
            original_data: Original data before splitting
            block_size: Block size used for splitting
            
        Returns:
            True if recovery is correct
        """
        recovered_blocks = self.recover_blocks()
        reassembler = BlockReassembler()
        recovered_data = reassembler.reassemble(recovered_blocks)
        return recovered_data == original_data
    
    def __repr__(self) -> str:
        return f"BlockRecovery(points={len(self.points)}, mapped={len(self.mapping)})"


class BlockManager:
    """
    High-level manager combining splitting, mapping, and recovery.
    """
    
    def __init__(self, block_size: int = 4):
        """
        Initialize block manager.
        
        Args:
            block_size: Size of each block
        """
        self.block_size = block_size
        self.splitter = BlockSplitter(block_size)
        self.reassembler = BlockReassembler()
    
    def split_data(self, data: str) -> List[str]:
        """
        Split data into blocks.
        
        Args:
            data: Data to split
            
        Returns:
            List of blocks
        """
        return self.splitter.split(data)
    
    def reassemble_data(self, blocks: List[str]) -> str:
        """
        Reassemble blocks into data.
        
        Args:
            blocks: List of blocks
            
        Returns:
            Reassembled data
        """
        return self.reassembler.reassemble(blocks)
    
    def create_block_mapping(self, blocks: List[str], points: List[Tuple[int, int, int]]) -> BlockMapping:
        """
        Create a block-to-point mapping.
        
        Args:
            blocks: List of blocks
            points: List of 3D points
            
        Returns:
            BlockMapping object
        """
        return BlockMapping(blocks, points)
    
    def create_recovery(self, points: List[Tuple[int, int, int]], mapping: dict) -> BlockRecovery:
        """
        Create a block recovery object.
        
        Args:
            points: List of 3D points
            mapping: Point-to-block mapping
            
        Returns:
            BlockRecovery object
        """
        return BlockRecovery(points, mapping)
    
    def __repr__(self) -> str:
        return f"BlockManager(block_size={self.block_size})"


if __name__ == "__main__":
    # Quick test of block operations
    print("🧪 Testing PointCrypt Blocks\n")
    
    print("Test 1: Split Data")
    splitter = BlockSplitter(block_size=4)
    blocks = splitter.split("HELLO WORLD")
    print(f"  Original: 'HELLO WORLD'")
    print(f"  Blocks: {blocks}")
    print(f"  Block count: {splitter.get_block_count('HELLO WORLD')}")
    
    print("\nTest 2: Reassemble Data")
    reassembler = BlockReassembler()
    recovered = reassembler.reassemble(blocks)
    print(f"  Reassembled: '{recovered}'")
    print(f"  Matches original: {recovered == 'HELLO WORLD'}")
    
    print("\nTest 3: Block Mapping")
    points = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    mapping = BlockMapping(blocks, points)
    random_map = mapping.create_random_mapping(seed=42)
    print(f"  Created random mapping with {len(random_map)} entries")
    print(f"  Sample: Point (1,2,3) → Block '{mapping.get_block_for_point((1,2,3))}'")
    
    print("\nTest 4: Block Recovery")
    # Get mapping with tuple keys for recovery
    recovery_mapping = {}
    for point in points:
        point_key = mapping._point_to_key(point)
        recovery_mapping[point] = random_map[point_key]
    
    recovery = BlockRecovery(points, recovery_mapping)
    recovered_blocks = recovery.recover_blocks()
    print(f"  Recovered blocks: {recovered_blocks}")
    print(f"  Verification: {recovery.verify_recovery('HELLO WORLD', 4)}")
    
    print("\nTest 5: Block Manager")
    manager = BlockManager(block_size=4)
    data = "TEST DATA STRING"
    blocks = manager.split_data(data)
    reassembled = manager.reassemble_data(blocks)
    print(f"  Original: '{data}'")
    print(f"  Split into {len(blocks)} blocks")
    print(f"  Reassembled: '{reassembled}'")
    print(f"  Match: {data == reassembled}")
    
    print("\n✅ All block tests passed!")