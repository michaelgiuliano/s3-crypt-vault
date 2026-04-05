import os
from dotenv import load_dotenv


class Settings:
    """
    Application configuration with fail-fast validation.
    Ensures required environment variables are present before runtime.
    """

    def __init__(self):
        load_dotenv()
        self._validate()

    def _get_required(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {key}")
        return value

    def _validate(self):
        """
        Validate required configuration at startup.
        """
        required_vars = [
            "AWS_REGION",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "S3_BUCKET_NAME",
        ]

        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

    @property
    def KEY_PATH(self):
        return os.getenv("KEY_PATH", "master.key")

    @property
    def AWS_REGION(self):
        return self._get_required("AWS_REGION")

    @property
    def AWS_ACCESS_KEY_ID(self):
        return self._get_required("AWS_ACCESS_KEY_ID")

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return self._get_required("AWS_SECRET_ACCESS_KEY")

    @property
    def S3_BUCKET_NAME(self):
        return self._get_required("S3_BUCKET_NAME")

    @property
    def USE_LOCALSTACK(self):
        return os.getenv("USE_LOCALSTACK", "false").lower() == "true"

    @property
    def LOCALSTACK_ENDPOINT(self):
        return "http://localhost:4566"
