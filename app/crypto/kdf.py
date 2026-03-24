from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit key from a password using scrypt.

    Parameters:
        password: user-provided password
        salt: random 16-byte salt

    Returns:
        32-byte key (AES-256)
    """

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )

    return kdf.derive(password.encode("utf-8"))