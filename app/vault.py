from pathlib import Path
from getpass import getpass

from app.encryptor import FileEncryptor
from app.s3_client import S3Client
from app.config import Settings
from app.crypto.envelope import encrypt as encrypt_v2, decrypt as decrypt_v2

class CryptVault:
    """
    Core vault logic.
    Handles encryption/decryption and interaction with S3 storage.
    """

    def __init__(self, key_path: str = "master.key"):
        self.settings = Settings()
        self.encryptor = FileEncryptor.load_key(key_path)

        settings = Settings()
        self.s3 = S3Client(settings)

    def _get_password(self) -> str:
        return getpass("Enter password: ")

    def upload_file(self, file_path: str):
        """
        Encrypt a file locally (v2) and upload it to S3.
        """

        path = Path(file_path)
        data = path.read_bytes()

        password = self._get_password()

        encrypted = encrypt_v2(password, data)

        object_key = f"{path.name}.enc"

        self.s3.upload_bytes(object_key, encrypted)

        return object_key

    def download_file(self, object_key: str, output_path: str):
        """
        Download encrypted object from S3 and decrypt locally.
        """

        encrypted = self.s3.download_bytes(object_key)

        if encrypted.startswith(b"SCV2"):
            # v2
            password = self._get_password()
            decrypted = decrypt_v2(password, encrypted)
        else:
            # v1 (legacy)
            decrypted = self.encryptor.decrypt(encrypted)

        Path(output_path).write_bytes(decrypted)

        return output_path