import os
import pytest

from app.encryptor import FileEncryptor
from app.vault import CryptVault
from app.crypto.envelope import encrypt as encrypt_v2


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

    object_key = vault.upload_file(str(test_file))

    output_file = tmp_path / "downloaded.txt"

    vault.download_file(object_key, str(output_file))

    downloaded_content = output_file.read_bytes()

    assert downloaded_content == original_content


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


def test_v2_flow(vault, tmp_path, monkeypatch):
    monkeypatch.setattr(vault, "_get_password", lambda: "test-password")

    data = b"hello"
    encrypted = encrypt_v2("test-password", data)

    key = "v2.enc"
    vault.s3.upload_bytes(key, encrypted)

    output = tmp_path / "out.txt"
    vault.download_file(key, str(output))

    assert output.read_bytes() == data