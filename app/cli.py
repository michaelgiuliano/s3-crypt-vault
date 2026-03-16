import typer

from app.encryptor import FileEncryptor
from app.vault import CryptVault
from app.s3_client import S3Client

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

    s3 = S3Client()

    if s3.bucket_exists():
        typer.echo(f"Bucket '{s3.bucket}' already exists.")
        raise typer.Exit()

    s3.create_bucket()

    typer.echo(f"Bucket '{s3.bucket}' created successfully.")


@app.command()
def upload(file: str, key_path: str = "master.key"):
    """
    Encrypt a file and upload it to S3.
    """

    vault = CryptVault(key_path=key_path)

    if not vault.s3.bucket_exists():
        typer.echo(
            f"Bucket '{vault.s3.bucket}' does not exist.\n"
            f"Create it first with: python -m app.cli create-bucket"
        )
        raise typer.Exit(code=1)

    object_key = vault.upload_file(file)

    typer.echo(f"Encrypted file uploaded as: {object_key}")


@app.command()
def download(object_key: str, output: str, key_path: str = "master.key"):
    """
    Download encrypted object from S3 and decrypt it.
    """

    vault = CryptVault(key_path=key_path)

    vault.download_file(object_key, output)

    typer.echo(f"File downloaded and decrypted to: {output}")


if __name__ == "__main__":
    app()