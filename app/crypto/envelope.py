import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.crypto.kdf import derive_key


DEK_SIZE = 32
GCM_TAG_SIZE = 16
ENC_DEK_SIZE = DEK_SIZE + GCM_TAG_SIZE
MIN_SIZE = 16 + 12 + 12 + ENC_DEK_SIZE


def encrypt(password: str, data: bytes) -> bytes:
    """
    Encrypt data using envelope encryption.
    Returns a raw blob (temporary format for v0.2.0 commit 1).
    """

    # Layout (temporary v0.2.0):
    # [0:16]   salt
    # [16:28]  dek_nonce
    # [28:40]  file_nonce
    # [40:?]   enc_dek (48 bytes)
    # [?]      ciphertext

    salt = os.urandom(16)
    master_key = derive_key(password, salt)

    dek = AESGCM.generate_key(bit_length=256)

    file_nonce = os.urandom(12)
    file_cipher = AESGCM(dek)
    ciphertext = file_cipher.encrypt(file_nonce, data, None)

    dek_nonce = os.urandom(12)
    dek_cipher = AESGCM(master_key)
    enc_dek = dek_cipher.encrypt(dek_nonce, dek, None)

    # --- TEMP FORMAT (commit 1) ---
    # salt | dek_nonce | file_nonce | enc_dek | ciphertext
    return salt + dek_nonce + file_nonce + enc_dek + ciphertext


def decrypt(password: str, blob: bytes) -> bytes:
    """
    Decrypt data using envelope encryption.
    """

    if len(blob) < MIN_SIZE:
        raise ValueError("Invalid encrypted data (too short)")

    salt = blob[:16]
    dek_nonce = blob[16:28]
    file_nonce = blob[28:40]

    enc_dek = blob[40:40 + ENC_DEK_SIZE]
    ciphertext = blob[40 + ENC_DEK_SIZE:]

    master_key = derive_key(password, salt)

    dek_cipher = AESGCM(master_key)
    dek = dek_cipher.decrypt(dek_nonce, enc_dek, None)

    file_cipher = AESGCM(dek)
    plaintext = file_cipher.decrypt(file_nonce, ciphertext, None)

    return plaintext