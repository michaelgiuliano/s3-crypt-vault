import os
import pytest

from app.encryptor import FileEncryptor
from app.exceptions import DecryptionError, PasswordRequiredError
from app.vault import CryptVault


@pytest.fixture
def vault(tmp_path):

    os.environ["USE_LOCALSTACK"] = "true"
    os.environ["S3_BUCKET_NAME"] = "test-vault"

    key_file = tmp_path / "test.key"

    encryptor = FileEncryptor()
    encryptor.save_key(key_file)

    return CryptVault(key_path=key_file)


def test_vault_encrypt_upload_download(vault, tmp_path):
    test_file = tmp_path / "secret.txt"
    original_content = b"super secret vault data"
    test_file.write_bytes(original_content)

    object_key = "secret.txt.enc"
    vault.upload_file(str(test_file), object_key, "test-password")

    output_file = tmp_path / "downloaded.txt"
    vault.download_file(object_key, str(output_file), "test-password")

    assert output_file.read_bytes() == original_content


def test_backward_compatibility(vault, tmp_path):

    test_file = tmp_path / "legacy.txt"
    content = b"legacy data"
    test_file.write_bytes(content)

    # v1 (legacy)
    encrypted = vault.encryptor.encrypt(content)
    key = "legacy.enc"
    vault.s3.upload_bytes(key, encrypted)

    output = tmp_path / "out.txt"
    vault.download_file(key, str(output))

    assert output.read_bytes() == content


def test_v2_flow(vault, tmp_path):
    data = b"hello"

    object_key = "file.txt.enc"
    vault.upload_bytes(object_key, data, "test-password")
    output = tmp_path / "out.txt"

    vault.download_file(object_key, str(output), "test-password")

    assert output.read_bytes() == data


def test_v2_requires_password(vault):
    data = b"secret"
    encrypted = vault.encrypt_bytes(data, "test-password")

    with pytest.raises(PasswordRequiredError):
        vault.decrypt_bytes(encrypted)


def test_v2_wrong_password(vault):
    data = b"secret"
    encrypted = vault.encrypt_bytes(data, "correct-password")

    with pytest.raises(DecryptionError):
        vault.decrypt_bytes(encrypted, "wrong-password")


def test_upload_file_not_found(vault):
    with pytest.raises(FileNotFoundError):
        vault.upload_file("nonexistent.txt", "nonexistent.txt.enc", "password")
