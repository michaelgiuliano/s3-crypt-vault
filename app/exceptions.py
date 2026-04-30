class VaultError(Exception):
    """Base exception for vault-related errors."""
    pass


class DecryptionError(VaultError):
    """Raised when decryption fails."""
    pass


class StorageError(VaultError):
    """Raised for storage-related failures."""
    pass
