import boto3
from app.config import Settings


settings = Settings()


class S3Client:
    """
    Wrapper around boto3 S3 client.
    Supports both AWS and LocalStack environments.
    """

    def __init__(self):

        self.bucket = settings.S3_BUCKET_NAME
        region = settings.AWS_REGION

        endpoint_url = None
        if settings.USE_LOCALSTACK:
            endpoint_url = settings.LOCALSTACK_ENDPOINT

        self.client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def upload_bytes(self, key: str, data: bytes):
        """
        Upload raw bytes to S3.
        """
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
        )

    def download_bytes(self, key: str) -> bytes:
        """
        Download object from S3 and return bytes.
        """

        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key,
        )

        return response["Body"].read()

    def bucket_exists(self) -> bool:

        buckets = self.client.list_buckets().get("Buckets", [])

        return any(b["Name"] == self.bucket for b in buckets)

    def create_bucket(self):

        if not self.bucket_exists():

            region = settings.AWS_REGION

            self.client.create_bucket(
                Bucket=self.bucket,
                CreateBucketConfiguration={"LocationConstraint": region},
            )