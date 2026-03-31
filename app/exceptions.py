class VaultError(Exception):
    """Base exception for vault-related errors."""
    pass


class PasswordRequiredError(VaultError):
    """Raised when a password is required but not provided."""
    pass


class DecryptionError(VaultError):
    """Raised when decryption fails."""
    pass


class StorageError(VaultError):
    """Raised for storage-related failures."""
    pass
