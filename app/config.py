import os
from dotenv import load_dotenv


load_dotenv()


class Settings:

    @property
    def AWS_REGION(self):
        return os.getenv("AWS_REGION")

    @property
    def AWS_ACCESS_KEY_ID(self):
        return os.getenv("AWS_ACCESS_KEY_ID")

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return os.getenv("AWS_SECRET_ACCESS_KEY")

    @property
    def S3_BUCKET_NAME(self):
        return os.getenv("S3_BUCKET_NAME")

    @property
    def USE_LOCALSTACK(self):
        return os.getenv("USE_LOCALSTACK", "false").lower() == "true"

    @property
    def LOCALSTACK_ENDPOINT(self):
        return "http://localhost:4566"