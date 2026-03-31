import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import Settings
from app.exceptions import StorageError


class S3Client:
    """
    Wrapper around boto3 S3 client.
    Supports both AWS and LocalStack environments.
    Adds basic error handling for clearer failure modes.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.bucket = settings.S3_BUCKET_NAME

        endpoint_url = (
            settings.LOCALSTACK_ENDPOINT if settings.USE_LOCALSTACK else None
        )

        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def upload_bytes(self, key: str, data: bytes):
        """
        Upload raw bytes to S3.
        """
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
            )
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to upload object '{key}' to S3: {e}") from e

    def download_bytes(self, key: str) -> bytes:
        """
        Download object from S3 and return bytes.
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key,
            )
            return response["Body"].read()
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to download object '{key}' from S3: {e}") from e

    def bucket_exists(self) -> bool:
        try:
            buckets = self.client.list_buckets().get("Buckets", [])
            return any(b["Name"] == self.bucket for b in buckets)
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to check if bucket exists: {e}") from e

    def create_bucket(self):
        try:
            if not self.bucket_exists():
                self.client.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={
                        "LocationConstraint": self.settings.AWS_REGION
                    },
                )
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to create bucket '{self.bucket}': {e}") from e

    def list_buckets(self):
        try:
            response = self.client.list_buckets()
            return [b["Name"] for b in response.get("Buckets", [])]
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to list S3 buckets: {e}") from e

    def list_objects(self):
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket)
            return [o["Key"] for o in response.get("Contents", [])]
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to list objects in bucket '{self.bucket}': {e}") from e