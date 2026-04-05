from pathlib import Path
from cryptography.exceptions import InvalidTag

from app.encryptor import FileEncryptor
from app.s3_client import S3Client
from app.config import Settings
from app.crypto.envelope import encrypt as encrypt_v2, decrypt as decrypt_v2
from app.exceptions import PasswordRequiredError, DecryptionError


class CryptVault:
    """
    Core vault logic.
    Handles encryption/decryption and interaction with S3 storage.
    """

    def __init__(self, s3: S3Client, encryptor: FileEncryptor):
        self.s3 = s3
        self.encryptor = encryptor

    def encrypt_bytes(self, data: bytes, password: str) -> bytes:
        return encrypt_v2(password, data)

    def decrypt_bytes(self, encrypted: bytes, password: str | None = None) -> bytes:
        if encrypted.startswith(b"SCV2"):
            if not password:
                raise PasswordRequiredError("Password required for v2 encrypted file")
            try:
                return decrypt_v2(password, encrypted)
            except InvalidTag:
                raise DecryptionError("Invalid password or corrupted data")
        else:
            try:
                return self.encryptor.decrypt(encrypted)
            except InvalidTag:
                raise DecryptionError("Invalid key or corrupted data")

    def upload_bytes(self, object_key: str, data: bytes, password: str) -> None:
        encrypted = self.encrypt_bytes(data, password)
        self.s3.upload_bytes(object_key, encrypted)

    def download_bytes(self, object_key: str, password: str | None = None) -> bytes:
        encrypted = self.s3.download_bytes(object_key)
        return self.decrypt_bytes(encrypted, password)

    def upload_file(self, file_path: str, object_key: str, password: str) -> None:
        data = Path(file_path).read_bytes()
        self.upload_bytes(object_key, data, password)

    def download_file(self, object_key: str, output_path: str, password: str | None = None):
        data = self.download_bytes(object_key, password)

        Path(output_path).write_bytes(data)

        return output_path
