import pytest
from cryptography.exceptions import InvalidTag

from app.crypto.envelope import encrypt, decrypt


def test_tamper_detection():
    """Verify that GCM detects if even a single bit of ciphertext changes."""
    encrypted = encrypt("test-password", b"Pure Data")

    corrupted_data = bytearray(encrypted)
    corrupted_data[-1] = (corrupted_data[-1] + 1) % 256

    with pytest.raises(InvalidTag):
        decrypt("test-password", bytes(corrupted_data))


def test_envelope_encrypt_decrypt_roundtrip():
    password = "strong-password"
    data = b"vault secret data"

    encrypted = encrypt(password, data)
    decrypted = decrypt(password, encrypted)

    assert decrypted == data


def test_invalid_magic_header():
    password = "test"
    data = b"hello"

    encrypted = encrypt(password, data)

    corrupted = b"XXXX" + encrypted[4:]

    with pytest.raises(ValueError):
        decrypt(password, corrupted)


def test_invalid_version():
    password = "test"
    data = b"hello"

    encrypted = encrypt(password, data)

    corrupted = encrypted[:4] + b"\x03" + encrypted[5:]

    with pytest.raises(ValueError):
        decrypt(password, corrupted)


def test_aad_tampering_detected():
    password = "test"
    data = b"hello"

    encrypted = encrypt(password, data)

    corrupted = bytearray(encrypted)
    corrupted[-1] ^= 0x01

    with pytest.raises(InvalidTag):
        decrypt(password, bytes(corrupted))
