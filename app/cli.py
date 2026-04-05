import typer
from getpass import getpass
from pathlib import Path

from app.encryptor import FileEncryptor
from app.vault import CryptVault
from app.s3_client import S3Client
from app.config import Settings
from app.exceptions import PasswordRequiredError


app = typer.Typer(help="S3 Crypt Vault CLI")


@app.command()
def init_key(path: str = "master.key"):
    """
    Generate a new encryption key.
    """

    encryptor = FileEncryptor()
    encryptor.save_key(path)

    typer.echo(f"Encryption key generated at: {path}")


@app.command()
def create_bucket():
    """
    Create the configured S3 bucket.
    """

    settings = Settings()
    s3 = S3Client(settings)

    if s3.bucket_exists():
        typer.echo(f"Bucket '{s3.bucket}' already exists.")
        raise typer.Exit()

    s3.create_bucket()

    typer.echo(f"Bucket '{s3.bucket}' created successfully.")


@app.command()
def list_buckets():
    """List available S3 buckets."""

    settings = Settings()
    s3 = S3Client(settings)

    buckets = s3.list_buckets()

    for b in buckets:
        typer.echo(b)


@app.command()
def list_files():
    """List encrypted files in the configured bucket."""

    settings = Settings()
    s3 = S3Client(settings)

    if not s3.bucket_exists():
        typer.echo(f"Bucket '{s3.bucket}' does not exist.")
        raise typer.Exit(1)

    objects = s3.list_objects()

    for obj in objects:
        typer.echo(obj)


@app.command()
def upload(file: str, key_path: str = "master.key"):
    """
    Encrypt a file and upload it to S3.
    """
    vault = CryptVault(key_path=key_path)

    if not vault.s3.bucket_exists():
        typer.echo(
            f"Bucket '{vault.s3.bucket}' does not exist.\n"
            f"Create it first with: s3vault create-bucket"
        )
        raise typer.Exit(code=1)

    password = getpass("Enter password: ")
    object_key = f"{Path(file).name}.enc"
    vault.upload_file(file, object_key, password)

    typer.echo(f"Encrypted file uploaded as: {object_key}")


@app.command()
def download(object_key: str, output: str, key_path: str = "master.key"):
    """
    Download encrypted object from S3 and decrypt it.
    """

    vault = CryptVault(key_path=key_path)

    try:
        vault.download_file(object_key, output)
    except PasswordRequiredError:
        typer.echo("Password required for encrypted file.")

        password = getpass("Enter password: ")
        vault.download_file(object_key, output, password)

    typer.echo(f"File downloaded and decrypted to: {output}")


if __name__ == "__main__":
    app()
