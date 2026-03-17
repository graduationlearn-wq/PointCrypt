"""
PointCrypt Sender Module

Handles encryption of data on the sender side.
"""

from .encryptor import (
    PointCryptEncryptor,
    EncryptionStructure,
    EncryptionResult,
)

__all__ = [
    'PointCryptEncryptor',
    'EncryptionStructure',
    'EncryptionResult',
]

__version__ = '1.0.0'