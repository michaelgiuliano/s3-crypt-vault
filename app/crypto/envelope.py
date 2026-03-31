import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.crypto.kdf import derive_key


DEK_SIZE = 32
GCM_TAG_SIZE = 16
ENC_DEK_SIZE = DEK_SIZE + GCM_TAG_SIZE
MIN_SIZE = 16 + 12 + 12 + ENC_DEK_SIZE

MAGIC = b"SCV2"
VERSION = 2

AAD = MAGIC + bytes([VERSION])


def encrypt(password: str, data: bytes) -> bytes:
    """
    Encrypt data using envelope encryption.
    Returns SCV2 structured binary format.
    """

    # Layout (temporary v0.2.0):
    # magic (4)        → b"SCV2"
    # version (1)      → 0x02
    # salt (16)
    # dek_nonce (12)
    # enc_dek_len (2)  → big endian
    # enc_dek (n)
    # file_nonce (12)
    # ciphertext (+ tag)

    salt = os.urandom(16)
    master_key = derive_key(password, salt)

    dek = AESGCM.generate_key(bit_length=256)

    file_nonce = os.urandom(12)
    ciphertext = AESGCM(dek).encrypt(file_nonce, data, AAD)

    dek_nonce = os.urandom(12)
    enc_dek = AESGCM(master_key).encrypt(dek_nonce, dek, AAD)

    enc_dek_len = len(enc_dek).to_bytes(2, "big")

    return (
        MAGIC +
        bytes([VERSION]) +
        salt +
        dek_nonce +
        enc_dek_len +
        enc_dek +
        file_nonce +
        ciphertext
    )


def decrypt(password: str, blob: bytes) -> bytes:
    """
    Decrypt data using envelope encryption.
    """

    if len(blob) < 4 + 1:
        raise ValueError("Invalid data")

    magic = blob[:4]
    if magic != MAGIC:
        raise ValueError("Invalid magic header")

    version = blob[4]
    if version != VERSION:
        raise ValueError(f"Unsupported version: {version}")

    offset = 5

    aad = magic + bytes([version])

    # --- salt ---
    salt = blob[offset:offset + 16]
    offset += 16

    # --- dek nonce ---
    dek_nonce = blob[offset:offset + 12]
    offset += 12

    # --- enc_dek length ---
    enc_dek_len = int.from_bytes(blob[offset:offset + 2], "big")
    offset += 2

    if len(blob) < offset + enc_dek_len + 12:
        raise ValueError("Invalid encrypted data (truncated enc_dek)")

    if enc_dek_len < ENC_DEK_SIZE:
        raise ValueError("Invalid enc_dek length")

    # --- enc_dek ---
    enc_dek = blob[offset:offset + enc_dek_len]
    offset += enc_dek_len

    # --- file nonce ---
    file_nonce = blob[offset:offset + 12]
    offset += 12

    ciphertext = blob[offset:]

    if len(ciphertext) == 0:
        raise ValueError("Invalid encrypted data (empty ciphertext)")

    # --- derive master key ---
    master_key = derive_key(password, salt)

    # --- decrypt DEK ---
    dek = AESGCM(master_key).decrypt(dek_nonce, enc_dek, aad)

    # --- decrypt file ---
    plaintext = AESGCM(dek).decrypt(file_nonce, ciphertext, aad)

    return plaintext
