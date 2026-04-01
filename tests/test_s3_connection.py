import boto3
import pytest
from botocore.exceptions import ClientError


@pytest.fixture
def s3_client():
    """
    Setup S3 client for LocalStack with cleanup.
    """
    region = "eu-north-1"
    client = boto3.client(
        's3',
        endpoint_url="http://localhost:4566",
        region_name=region,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )
    yield client

    # Teardown: Remove the bucket after the test to keep LocalStack clean
    try:
        client.delete_bucket(Bucket="test-vault")
    except ClientError:
        pass


def test_s3_connection_localstack(s3_client):
    region = "eu-north-1"
    bucket_name = "test-vault"

    # Check if bucket exists before creating
    # This prevents 'BucketAlreadyOwnedByYou' errors
    existing_buckets = [b['Name'] for b in s3_client.list_buckets().get('Buckets', [])]

    if bucket_name not in existing_buckets:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    # Final check to verify it actually exists now
    response = s3_client.list_buckets()
    buckets = [b['Name'] for b in response.get('Buckets', [])]

    assert bucket_name in buckets
