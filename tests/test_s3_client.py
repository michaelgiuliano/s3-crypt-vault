import os
import pytest

from app.s3_client import S3Client
from app.config import Settings


@pytest.fixture
def s3_client():
    os.environ["USE_LOCALSTACK"] = "true"
    os.environ["S3_BUCKET_NAME"] = "test-vault"

    settings = Settings()
    client = S3Client(settings)
    client.create_bucket()

    yield client

    for key in client.list_objects():
        client.client.delete_object(Bucket=client.bucket, Key=key)


def test_upload_download_cycle(s3_client):

    key = "test-object.txt"
    data = b"hello encrypted world"

    s3_client.upload_bytes(key, data)

    downloaded = s3_client.download_bytes(key)

    assert downloaded == data
