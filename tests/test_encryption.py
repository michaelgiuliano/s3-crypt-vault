import pytest
from cryptography.exceptions import InvalidTag

from app.encryptor import FileEncryptor
from app.crypto.envelope import encrypt, decrypt


def test_encryption_decryption_workflow():
    """Verify that data remains consistent after an enc/dec cycle."""
    encryptor = FileEncryptor()
    secret_message = b"Secret Norwegian Waffle Recipe v1"

    encrypted = encryptor.encrypt(secret_message)
    assert encrypted != secret_message
    
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == secret_message


def test_key_persistence(tmp_path):
    """Verify the key can be saved and reloaded using a temporary directory."""
    key_file = tmp_path / "test.key"
    original_encryptor = FileEncryptor()
    original_encryptor.save_key(key_file)

    new_encryptor = FileEncryptor.load_key(key_file)
    assert original_encryptor.key == new_encryptor.key


def test_tamper_detection():
    """Verify that GCM detects if even a single bit of ciphertext changes."""
    encryptor = FileEncryptor()
    encrypted = encryptor.encrypt(b"Pure Data")

    corrupted_data = bytearray(encrypted)
    corrupted_data[-1] = (corrupted_data[-1] + 1) % 256

    with pytest.raises(InvalidTag):
        encryptor.decrypt(bytes(corrupted_data))


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