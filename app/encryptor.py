"""
LEGACY MODULE (v1)

Single-key AES-GCM encryption.
Kept for backward compatibility.

v2 uses envelope encryption (see app.crypto.envelope).
"""

import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class FileEncryptor:
    """
    DEPRECATED (v1)

    This class implements single-key encryption.
    Use envelope encryption for new data.
    
    Handles AES-256 GCM encryption and decryption.
    Ensures both data confidentiality and integrity (AEAD).
    """

    def __init__(self, key: bytes = None):
        """
        Initialize with a 256-bit key or generate a new one.
        """
        self.key = key or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts plaintext and prepends a 12-byte random nonce.
        """
        nonce = os.urandom(12)  # Standard GCM nonce size
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Extracts the nonce and decrypts the ciphertext.
        Raises InvalidTag if data is tampered with.
        """
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    def save_key(self, path: str | Path = "master.key") -> None:
        """
        Persists the master key to a local file with restricted permissions (0o600).
        """
        key_path = Path(path)
        with key_path.open("wb") as f:
            f.write(self.key)
        
        # Security: Only the owner can read/write this file
        key_path.chmod(0o600)

    @classmethod
    def load_key(cls, path: str | Path = "master.key") -> "FileEncryptor":
        """
        Factory method to create an encryptor from an existing key file.
        """
        key_path = Path(path)
        if not key_path.exists():
            raise FileNotFoundError(f"Key file not found at: {path}")
        
        return cls(key=key_path.read_bytes())
    
    @staticmethod
    def is_legacy_format(data: bytes) -> bool:
        """
        Heuristic: v1 has no header, raw nonce + ciphertext.
        """
        return True  # placeholder