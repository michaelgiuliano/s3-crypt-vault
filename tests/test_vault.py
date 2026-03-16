import os
import pytest

from app.encryptor import FileEncryptor
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

    object_key = vault.upload_file(str(test_file))

    output_file = tmp_path / "downloaded.txt"

    vault.download_file(object_key, str(output_file))

    downloaded_content = output_file.read_bytes()

    assert downloaded_content == original_content