"""
PointCrypt Core Module

Contains fundamental cryptographic utilities and formulas.
"""

from .utils import (
    secure_hash,
    hash_to_int,
    combine_factors,
    bitshift_operation,
    xor_operation,
    polynomial_mod,
    coordinate_conversion,
    validate_seed,
    validate_block_count,
    PRIME_MODULUS,
    COORDINATE_RANGE,
)

from .formulas import (
    SequencingFormula,
    MainFormula,
    PointCryptFormulas,
)

from .blocks import (
    BlockSplitter,
    BlockReassembler,
    BlockMapping,
    BlockRecovery,
    BlockManager,
)

__all__ = [
    # Utils
    'secure_hash',
    'hash_to_int',
    'combine_factors',
    'bitshift_operation',
    'xor_operation',
    'polynomial_mod',
    'coordinate_conversion',
    'validate_seed',
    'validate_block_count',
    'PRIME_MODULUS',
    'COORDINATE_RANGE',
    # Formulas
    'SequencingFormula',
    'MainFormula',
    'PointCryptFormulas',
    # Blocks
    'BlockSplitter',
    'BlockReassembler',
    'BlockMapping',
    'BlockRecovery',
    'BlockManager',
]

__version__ = '1.0.0'
__author__ = 'Arnav'
__description__ = 'Formula-based obfuscation system for learning cryptographic principles'