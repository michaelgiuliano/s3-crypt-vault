import os
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.dependencies import get_vault
from app.config import Settings
from app.encryptor import FileEncryptor
from app.s3_client import S3Client
from app.vault import CryptVault


@pytest.fixture
def vault(tmp_path):
    os.environ["USE_LOCALSTACK"] = "true"
    os.environ["S3_BUCKET_NAME"] = "test-vault"

    key_file = tmp_path / "test.key"
    encryptor = FileEncryptor()
    encryptor.save_key(key_file)

    settings = Settings()
    s3 = S3Client(settings)
    s3.create_bucket()

    yield CryptVault(s3=s3, encryptor=encryptor)

    for key in s3.list_objects():
        s3.client.delete_object(Bucket=s3.bucket, Key=key)


@pytest.fixture
def client(vault):
    app.dependency_overrides[get_vault] = lambda: vault
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_upload_download_roundtrip(client):
    content = b"secret api data"

    response = client.post(
        "/files",
        data={"password": "test-password"},
        files={"file": ("roundtrip.txt", content, "text/plain")},
    )
    assert response.status_code == 201
    object_key = response.json()["object_key"]
    assert object_key == "roundtrip.txt.enc"

    response = client.post(
        f"/files/{object_key}/download",
        json={"password": "test-password"},
    )
    assert response.status_code == 200
    assert response.content == content


def test_upload_duplicate_returns_409(client):
    content = b"some data"

    client.post(
        "/files",
        data={"password": "test-password"},
        files={"file": ("dupe.txt", content, "text/plain")},
    )

    response = client.post(
        "/files",
        data={"password": "test-password"},
        files={"file": ("dupe.txt", content, "text/plain")},
    )
    assert response.status_code == 409


def test_download_wrong_password_returns_400(client):
    content = b"protected data"

    client.post(
        "/files",
        data={"password": "correct-password"},
        files={"file": ("protected.txt", content, "text/plain")},
    )

    response = client.post(
        "/files/protected.txt.enc/download",
        json={"password": "wrong-password"},
    )
    assert response.status_code == 400


def test_download_missing_file_returns_404(client):
    response = client.post(
        "/files/nonexistent.txt.enc/download",
        json={"password": "any-password"},
    )
    assert response.status_code == 404


def test_list_files_returns_uploaded(client):
    content = b"listable data"

    client.post(
        "/files",
        data={"password": "test-password"},
        files={"file": ("listed.txt", content, "text/plain")},
    )

    response = client.get("/files")
    assert response.status_code == 200
    assert "listed.txt.enc" in response.json()["files"]