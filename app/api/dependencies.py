from fastapi import Depends

from app.config import Settings
from app.encryptor import FileEncryptor
from app.s3_client import S3Client
from app.vault import CryptVault


def get_settings() -> Settings:
    return Settings()


def get_s3_client(settings: Settings = Depends(get_settings)) -> S3Client:
    return S3Client(settings)


def get_vault(
    settings: Settings = Depends(get_settings),
    s3: S3Client = Depends(get_s3_client),
) -> CryptVault:

    encryptor = FileEncryptor.load_key(settings.KEY_PATH)
    return CryptVault(s3=s3, encryptor=encryptor)
