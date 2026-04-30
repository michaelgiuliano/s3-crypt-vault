from fastapi import Depends

from app.config import Settings
from app.s3_client import S3Client
from app.vault import CryptVault


def get_settings() -> Settings:
    return Settings()


def get_s3_client(settings: Settings = Depends(get_settings)) -> S3Client:
    return S3Client(settings)


def get_vault(
    s3: S3Client = Depends(get_s3_client),
) -> CryptVault:
    return CryptVault(s3=s3)
