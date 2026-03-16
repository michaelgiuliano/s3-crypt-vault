from pathlib import Path

from app.encryptor import FileEncryptor
from app.s3_client import S3Client


class CryptVault:
    """
    Core vault logic.
    Handles encryption/decryption and interaction with S3 storage.
    """

    def __init__(self, key_path: str = "master.key"):

        self.encryptor = FileEncryptor.load_key(key_path)
        self.s3 = S3Client()

    def upload_file(self, file_path: str):
        """
        Encrypt a file locally and upload it to S3.
        """

        path = Path(file_path)

        data = path.read_bytes()

        encrypted = self.encryptor.encrypt(data)

        object_key = f"{path.name}.enc"

        self.s3.upload_bytes(object_key, encrypted)

        return object_key

    def download_file(self, object_key: str, output_path: str):
        """
        Download encrypted object from S3 and decrypt locally.
        """

        encrypted = self.s3.download_bytes(object_key)

        decrypted = self.encryptor.decrypt(encrypted)

        Path(output_path).write_bytes(decrypted)

        return output_path