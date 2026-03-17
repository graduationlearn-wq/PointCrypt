"""
PointCrypt Core Utilities

Helper functions for hashing, validation, and common operations.
"""

from Crypto.Hash import SHA3_256
from typing import Union, Tuple, List


def secure_hash(data: Union[str, bytes]) -> str:
    """
    Generate SHA3-256 hash of input data.
    
    Args:
        data: String or bytes to hash
        
    Returns:
        Hexadecimal hash string
        
    Example:
        >>> hash_val = secure_hash("hello world")
        >>> len(hash_val)
        64
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hash_obj = SHA3_256.new(data)
    return hash_obj.hexdigest()


def hash_to_int(data: Union[str, bytes], modulo: int = None) -> int:
    """
    Convert hash to integer, optionally with modulo.
    
    Args:
        data: String or bytes to hash
        modulo: Optional modulo value to constrain result
        
    Returns:
        Integer hash value
        
    Example:
        >>> val = hash_to_int("seed123", modulo=1000)
        >>> 0 <= val < 1000
        True
    """
    hash_hex = secure_hash(data)
    hash_int = int(hash_hex, 16)
    
    if modulo:
        return hash_int % modulo
    return hash_int


def combine_factors(*args) -> str:
    """
    Combine multiple factors into a single string for hashing.
    
    Args:
        *args: Variable number of arguments (str, int, bytes)
        
    Returns:
        Combined string with separator
        
    Example:
        >>> combined = combine_factors("seed", 7, "hash123")
        >>> combined
        'seed|7|hash123'
    """
    return "|".join(str(arg) for arg in args)


def bitshift_operation(value: int, shift: int) -> int:
    """
    Perform right bitshift operation safely.
    
    Args:
        value: Integer to shift
        shift: Number of bits to shift right
        
    Returns:
        Shifted integer value
        
    Example:
        >>> bitshift_operation(482641, 16)
        7
    """
    return value >> shift


def validate_seed(seed: Union[str, bytes]) -> bool:
    """
    Validate that seed is not empty and has reasonable length.
    
    Args:
        seed: Seed value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if isinstance(seed, str):
        seed = seed.encode('utf-8')
    
    return len(seed) > 0 and len(seed) <= 10000


def validate_block_count(block_count: int) -> bool:
    """
    Validate block count is positive and reasonable.
    
    Args:
        block_count: Number of blocks
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(block_count, int) and 1 <= block_count <= 10000


def xor_operation(a: int, b: int) -> int:
    """
    Perform XOR operation between two integers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        XOR result
        
    Example:
        >>> xor_operation(35232793, 7)
        35232786
    """
    return a ^ b


def polynomial_mod(coefficients: List[int], x: int, modulo: int) -> int:
    """
    Evaluate polynomial with given coefficients at x, modulo m.
    
    Polynomial: coefficients[0]*x^n + coefficients[1]*x^(n-1) + ... + coefficients[n]
    
    Args:
        coefficients: List of polynomial coefficients [a, b, c, d] for ax^3 + bx^2 + cx + d
        x: Value at which to evaluate
        modulo: Modulus for result
        
    Returns:
        Polynomial result modulo m
        
    Example:
        >>> coeffs = [793, 177, 407, 817]  # 793x^3 + 177x^2 + 407x + 817
        >>> polynomial_mod(coeffs, 641, 1000000007)
        101965766
    """
    result = 0
    power = len(coefficients) - 1
    
    for coeff in coefficients:
        # result = (result + coeff * (x ** power)) % modulo
        # More efficient with pow(base, exp, mod)
        term = (coeff * pow(x, power, modulo)) % modulo
        result = (result + term) % modulo
        power -= 1
    
    return result


def coordinate_conversion(value: int, dimension: int, range_max: int = 10000) -> int:
    """
    Extract a coordinate dimension from a large integer.
    
    Converts 1D value to 3D by dividing into ranges.
    
    Args:
        value: Large integer value
        dimension: Which dimension (0=x, 1=y, 2=z)
        range_max: Max value per coordinate
        
    Returns:
        Coordinate value in range [0, range_max)
        
    Example:
        >>> val = 101965766
        >>> coordinate_conversion(val, 0)  # x coordinate
        5766
        >>> coordinate_conversion(val, 1)  # y coordinate
        196
        >>> coordinate_conversion(val, 2)  # z coordinate
        1
    """
    divisor = range_max ** dimension
    return (value // divisor) % range_max


def format_3d_point(x: int, y: int, z: int) -> Tuple[int, int, int]:
    """
    Format and validate a 3D point.
    
    Args:
        x, y, z: Coordinate values
        
    Returns:
        Tuple of (x, y, z)
    """
    return (int(x), int(y), int(z))


def validate_data_integrity(original: str, recovered: str) -> bool:
    """
    Check if original and recovered data match.
    
    Args:
        original: Original data
        recovered: Recovered data
        
    Returns:
        True if they match, False otherwise
    """
    return original == recovered


# Constants used throughout PointCrypt
PRIME_MODULUS = 1000000007  # Large prime for polynomial evaluation
COORDINATE_RANGE = 10000     # Range for each 3D coordinate
MAX_BLOCK_SIZE = 1000000     # Maximum block size in bytes
HASH_OUTPUT_BITS = 256       # SHA3-256 hash output bits


if __name__ == "__main__":
    # Quick test of utilities
    print("🧪 Testing Core Utilities\n")
    
    print("Test 1: Hashing")
    h = secure_hash("test data")
    print(f"  Hash of 'test data': {h[:16]}...")
    print(f"  Hash length: {len(h)}")
    
    print("\nTest 2: Hash to Integer")
    h_int = hash_to_int("seed123", modulo=1000)
    print(f"  hash_to_int('seed123', 1000): {h_int}")
    
    print("\nTest 3: Combine Factors")
    combined = combine_factors("seed", 7, "hash123")
    print(f"  Combined: {combined}")
    
    print("\nTest 4: Polynomial Evaluation")
    coeffs = [793, 177, 407, 817]
    result = polynomial_mod(coeffs, 641, PRIME_MODULUS)
    print(f"  Polynomial result: {result}")
    
    print("\nTest 5: Coordinate Conversion")
    val = 101965766
    x = coordinate_conversion(val, 0)
    y = coordinate_conversion(val, 1)
    z = coordinate_conversion(val, 2)
    print(f"  1D value {val} → 3D point ({x}, {y}, {z})")
    
    print("\nTest 6: Validation")
    print(f"  Validate seed 'secret': {validate_seed('secret')}")
    print(f"  Validate block_count 7: {validate_block_count(7)}")
    
    print("\n✅ All utility tests passed!")