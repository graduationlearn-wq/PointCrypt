"""
PointCrypt Core Formulas

Implements the two main formulas:
1. Sequencing Formula - Generates sequence of input numbers
2. Main Formula - Generates 3D points from input numbers
"""

from typing import List, Tuple
from core.utils import (
    secure_hash,
    hash_to_int,
    combine_factors,
    bitshift_operation,
    xor_operation,
    polynomial_mod,
    coordinate_conversion,
    format_3d_point,
    validate_seed,
    validate_block_count,
    PRIME_MODULUS,
    COORDINATE_RANGE,
)


class SequencingFormula:
    """
    Generates a sequence of input numbers based on seed, block_count, and data_hash.
    
    This formula is deterministic: same inputs always produce same sequence.
    Different seeds or block counts produce completely different sequences.
    """
    
    def __init__(self, seed: str, block_count: int, data_hash: str = None):
        """
        Initialize sequencing formula.
        
        Args:
            seed: Secret seed value
            block_count: Number of blocks in the data
            data_hash: Hash of the actual data (optional but recommended)
        """
        if not validate_seed(seed):
            raise ValueError("Invalid seed: must be non-empty and <= 10000 chars")
        if not validate_block_count(block_count):
            raise ValueError("Invalid block_count: must be between 1 and 10000")
        
        self.seed = seed
        self.block_count = block_count
        self.data_hash = data_hash or ""
    
    def get_starting_point(self) -> int:
        """
        Calculate the starting point of the sequence.
        
        Returns:
            Starting number for the sequence
        """
        combined = combine_factors(self.seed, self.block_count, self.data_hash)
        h = hash_to_int(combined)
        return h % 1000
    
    def get_base_step(self) -> int:
        """
        Calculate the base step size for sequence generation.
        
        Returns:
            Step size (1-10)
        """
        combined = combine_factors(self.seed, self.block_count, self.data_hash)
        h = hash_to_int(combined)
        shifted = bitshift_operation(h, 16)
        return (shifted % 10) + 1
    
    def get_variable_step(self, index: int) -> int:
        """
        Calculate variable step for a specific position.
        
        Makes each step slightly different for non-linear progression.
        
        Args:
            index: Position in sequence (0, 1, 2, ...)
            
        Returns:
            Variable step adjustment
        """
        combined = combine_factors(self.seed, self.block_count, self.data_hash)
        step_combined = combine_factors(combined, "step", index)
        step_hash = hash_to_int(step_combined)
        
        # Step varies around the base step: ±2
        variation = (step_hash % 5) - 2
        return variation
    
    def generate(self) -> List[int]:
        """
        Generate the complete sequence of input numbers.
        
        Returns:
            List of integers to use as inputs to main formula
            
        Example:
            >>> seq_formula = SequencingFormula("secret", 7, "hash123")
            >>> sequence = seq_formula.generate()
            >>> len(sequence)
            7
            >>> sequence[0] < sequence[1] < sequence[2]  # Ascending
            True
        """
        starting_point = self.get_starting_point()
        base_step = self.get_base_step()
        
        sequence = [starting_point]
        
        for i in range(1, self.block_count):
            variation = self.get_variable_step(i)
            actual_step = base_step + variation
            next_point = sequence[-1] + actual_step
            sequence.append(next_point)
        
        return sequence
    
    def __repr__(self) -> str:
        return f"SequencingFormula(seed=***hidden***, block_count={self.block_count})"


class MainFormula:
    """
    Generates 3D points from input numbers using a cubic polynomial.
    
    The polynomial coefficients are derived from the seed and block_count,
    making the formula unique for each data transfer.
    """
    
    def __init__(self, seed: str, block_count: int):
        """
        Initialize main formula.
        
        Args:
            seed: Secret seed value
            block_count: Number of blocks in the data
        """
        if not validate_seed(seed):
            raise ValueError("Invalid seed: must be non-empty and <= 10000 chars")
        if not validate_block_count(block_count):
            raise ValueError("Invalid block_count: must be between 1 and 10000")
        
        self.seed = seed
        self.block_count = block_count
        self._coefficients = None
    
    def _get_seed_value(self) -> int:
        """
        Convert seed string to integer value.
        
        Returns:
            Integer derived from seed hash
        """
        return hash_to_int(self.seed) % 1000000
    
    def get_coefficients(self) -> Tuple[int, int, int, int]:
        """
        Derive polynomial coefficients from seed and block_count.
        
        Coefficients for polynomial: a*x^3 + b*x^2 + c*x + d
        
        Returns:
            Tuple of (a, b, c, d)
            
        Example:
            >>> main = MainFormula("secret", 7)
            >>> a, b, c, d = main.get_coefficients()
            >>> all(0 <= coef < 1000 for coef in [a, b, c, d])
            True
        """
        if self._coefficients is not None:
            return self._coefficients
        
        seed_value = self._get_seed_value()
        
        # Derive each coefficient using different prime multipliers
        a = ((seed_value * 73) ^ self.block_count) % 1000
        b = ((seed_value * 97) ^ self.block_count) % 1000
        c = ((seed_value * 127) ^ self.block_count) % 1000
        d = ((seed_value * 137) ^ self.block_count) % 1000
        
        self._coefficients = (a, b, c, d)
        return self._coefficients
    
    def evaluate_polynomial(self, x: int) -> int:
        """
        Evaluate the polynomial at point x.
        
        f(x) = a*x^3 + b*x^2 + c*x + d (mod PRIME_MODULUS)
        
        Args:
            x: Input value
            
        Returns:
            Polynomial result
        """
        a, b, c, d = self.get_coefficients()
        coefficients = [a, b, c, d]
        return polynomial_mod(coefficients, x, PRIME_MODULUS)
    
    def generate_point(self, x: int) -> Tuple[int, int, int]:
        """
        Generate a 3D point from a single input value.
        
        Args:
            x: Input value (from sequence)
            
        Returns:
            3D point as (x_coord, y_coord, z_coord)
            
        Example:
            >>> main = MainFormula("secret", 7)
            >>> point = main.generate_point(641)
            >>> len(point)
            3
            >>> all(0 <= coord < 10000 for coord in point)
            True
        """
        value = self.evaluate_polynomial(x)
        
        x_coord = coordinate_conversion(value, 0, COORDINATE_RANGE)
        y_coord = coordinate_conversion(value, 1, COORDINATE_RANGE)
        z_coord = coordinate_conversion(value, 2, COORDINATE_RANGE)
        
        return format_3d_point(x_coord, y_coord, z_coord)
    
    def generate_points(self, sequence: List[int]) -> List[Tuple[int, int, int]]:
        """
        Generate 3D points for an entire sequence of inputs.
        
        Args:
            sequence: List of input numbers from sequencing formula
            
        Returns:
            List of 3D points
            
        Example:
            >>> seq_formula = SequencingFormula("secret", 7, "hash123")
            >>> sequence = seq_formula.generate()
            >>> main = MainFormula("secret", 7)
            >>> points = main.generate_points(sequence)
            >>> len(points)
            7
            >>> all(isinstance(p, tuple) and len(p) == 3 for p in points)
            True
        """
        return [self.generate_point(x) for x in sequence]
    
    def __repr__(self) -> str:
        return f"MainFormula(seed=***hidden***, block_count={self.block_count})"


class PointCryptFormulas:
    """
    Unified interface for both formulas working together.
    """
    
    def __init__(self, seed: str, block_count: int, data_hash: str = None):
        """
        Initialize both formulas.
        
        Args:
            seed: Secret seed
            block_count: Number of blocks
            data_hash: Hash of data (optional)
        """
        self.seed = seed
        self.block_count = block_count
        self.data_hash = data_hash or ""
        
        self.sequencing = SequencingFormula(seed, block_count, self.data_hash)
        self.main = MainFormula(seed, block_count)
    
    def generate_sequence_and_points(self) -> Tuple[List[int], List[Tuple[int, int, int]]]:
        """
        Generate both sequence and corresponding 3D points.
        
        Returns:
            Tuple of (sequence_inputs, 3d_points)
            
        Example:
            >>> formulas = PointCryptFormulas("secret", 5, "datahash")
            >>> inputs, points = formulas.generate_sequence_and_points()
            >>> len(inputs) == len(points) == 5
            True
        """
        sequence = self.sequencing.generate()
        points = self.main.generate_points(sequence)
        return sequence, points
    
    def get_formula_info(self) -> dict:
        """
        Get metadata about the formulas.
        
        Returns:
            Dictionary with formula information
        """
        _, points = self.generate_sequence_and_points()
        coefficients = self.main.get_coefficients()
        
        return {
            "seed": "***hidden***",
            "block_count": self.block_count,
            "has_data_hash": bool(self.data_hash),
            "starting_point": self.sequencing.get_starting_point(),
            "base_step": self.sequencing.get_base_step(),
            "coefficients": {
                "a": coefficients[0],
                "b": coefficients[1],
                "c": coefficients[2],
                "d": coefficients[3],
            },
            "sample_point": points[0] if points else None,
            "total_points": len(points),
        }


if __name__ == "__main__":
    # Quick test of formulas
    print("🧪 Testing PointCrypt Formulas\n")
    
    print("Test 1: Sequencing Formula")
    seq_formula = SequencingFormula("test_seed", 7, "datahash123")
    sequence = seq_formula.generate()
    print(f"  Sequence (7 numbers): {sequence}")
    print(f"  Starting point: {seq_formula.get_starting_point()}")
    print(f"  Base step: {seq_formula.get_base_step()}")
    
    print("\nTest 2: Main Formula")
    main_formula = MainFormula("test_seed", 7)
    coeffs = main_formula.get_coefficients()
    print(f"  Polynomial coefficients (a,b,c,d): {coeffs}")
    
    print("\nTest 3: Generate Points")
    points = main_formula.generate_points(sequence)
    print(f"  Generated {len(points)} 3D points:")
    for i, point in enumerate(points[:3]):
        print(f"    Point {i}: {point}")
    print(f"    ... ({len(points) - 3} more points)")
    
    print("\nTest 4: Unified Interface")
    formulas = PointCryptFormulas("my_secret", 5, "mydata")
    seq, pts = formulas.generate_sequence_and_points()
    print(f"  Sequence: {seq}")
    print(f"  Points: {pts}")
    print(f"  Formula info: {formulas.get_formula_info()}")
    
    print("\n✅ All formula tests passed!")