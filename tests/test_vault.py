import os
import pytest
from pathlib import Path

from app.exceptions import DecryptionError
from app.s3_client import S3Client
from app.vault import CryptVault
from app.config import Settings


@pytest.fixture
def vault():
    os.environ["USE_LOCALSTACK"] = "true"
    os.environ["S3_BUCKET_NAME"] = "test-vault"

    settings = Settings()
    s3 = S3Client(settings)
    s3.create_bucket()

    yield CryptVault(s3=s3)

    for key in s3.list_objects():
        s3.client.delete_object(Bucket=s3.bucket, Key=key)


@pytest.fixture
def test_files():
    test_dir = Path("tests/.tmp")
    test_dir.mkdir(exist_ok=True)

    for file_path in test_dir.iterdir():
        if file_path.is_file():
            file_path.unlink()

    yield test_dir

    for file_path in test_dir.iterdir():
        if file_path.is_file():
            file_path.unlink()


def test_vault_encrypt_upload_download(vault, test_files):
    test_file = test_files / "secret.txt"
    original_content = b"super secret vault data"
    test_file.write_bytes(original_content)

    object_key = "secret.txt.enc"
    vault.upload_file(str(test_file), object_key, "test-password")

    output_file = test_files / "downloaded.txt"
    vault.download_file(object_key, str(output_file), "test-password")

    assert output_file.read_bytes() == original_content


def test_v2_flow(vault, test_files):
    data = b"hello"

    object_key = "file.txt.enc"
    vault.upload_bytes(object_key, data, "test-password")
    output = test_files / "out.txt"

    vault.download_file(object_key, str(output), "test-password")

    assert output.read_bytes() == data


def test_unsupported_format_returns_decryption_error(vault):
    data = b"secret"

    with pytest.raises(DecryptionError):
        vault.decrypt_bytes(data, "test-password")


def test_v2_wrong_password(vault):
    data = b"secret"
    encrypted = vault.encrypt_bytes(data, "correct-password")

    with pytest.raises(DecryptionError):
        vault.decrypt_bytes(encrypted, "wrong-password")


def test_upload_file_not_found(vault):
    with pytest.raises(FileNotFoundError):
        vault.upload_file("nonexistent.txt", "nonexistent.txt.enc", "password")
