import pytest
from app.encryptor import FileEncryptor


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

    # Load into a new instance
    new_encryptor = FileEncryptor.load_key(key_file)
    assert original_encryptor.key == new_encryptor.key


def test_tamper_detection():
    """Verify that GCM detects if even a single bit of ciphertext changes."""
    encryptor = FileEncryptor()
    encrypted = encryptor.encrypt(b"Pure Data")

    # Manually corrupt the last byte of the ciphertext
    corrupted_data = bytearray(encrypted)
    corrupted_data[-1] = (corrupted_data[-1] + 1) % 256

    with pytest.raises(Exception):
        # AES-GCM will raise an InvalidTag exception here
        encryptor.decrypt(bytes(corrupted_data))