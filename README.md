# S3 Crypt Vault

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/michaelgiuliano/s3-crypt-vault/actions/workflows/ci.yml/badge.svg)

S3 Crypt Vault is a Python backend project that stores files in AWS S3 only after encrypting them locally.

The goal is simple: S3 stores encrypted bytes, while the application handles encryption and decryption before data leaves the client side.

## Architecture

```text
Client
  -> FastAPI routes
  -> CryptVault service
  -> Envelope encryption
  -> S3Client
  -> AWS S3 / LocalStack
```

### Main Components

- `app/api/`: FastAPI app, routes, schemas, dependencies, and HTTP error mapping.
- `app/vault.py`: service layer that coordinates encryption and S3 operations.
- `app/crypto/`: password-based envelope encryption and key derivation.
- `app/s3_client.py`: small wrapper around boto3 S3 operations.
- `app/cli.py`: command-line interface using the same vault logic.
- `tests/`: coverage for encryption, vault behavior, S3 integration, and API flows.

## Encryption Design

Files are encrypted with AES-256-GCM using envelope encryption:

1. The user provides a password.
2. A random salt is generated.
3. `scrypt` derives a 256-bit key from the password and salt.
4. A random data encryption key is generated for the file.
5. The file is encrypted with the data encryption key.
6. The data encryption key is encrypted with the password-derived key.
7. The encrypted file and encrypted data key are stored together as an `SCV2` blob.

AES-GCM provides both confidentiality and tamper detection. If the ciphertext is modified or the wrong password is used, decryption fails.

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/files` | List encrypted objects in the bucket |
| `POST` | `/files` | Upload and encrypt a file |
| `POST` | `/files/{key}/download` | Download and decrypt a file |

## Setup

Install dependencies:

```bash
pip install -e .
```

Create a `.env` file:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=eu-north-1
S3_BUCKET_NAME=your-bucket_name_here
USE_LOCALSTACK=true
```

For local development, start LocalStack:

```bash
docker-compose up -d
```

Create the configured bucket:

```bash
s3vault create-bucket
```

Run the API:

```bash
uvicorn app.api.main:app --reload
```

Interactive docs are available at `http://localhost:8000/docs`.

## CLI Usage

Upload a file:

```bash
s3vault upload secret.txt
```

List encrypted files:

```bash
s3vault list-files
```

Download and decrypt a file:

```bash
s3vault download secret.txt.enc decrypted.txt
```

## API Examples

Upload a file:

```bash
curl -X POST http://localhost:8000/files \
  -F "file=@secret.txt" \
  -F "password=your-password"
```

Download and decrypt a file:

```bash
curl -X POST http://localhost:8000/files/secret.txt.enc/download \
  -H "Content-Type: application/json" \
  -d '{"password": "your-password"}' \
  --output decrypted.txt
```

## Testing

Run the test suite:

```bash
pytest tests/
```

The tests cover:

- Envelope encryption round trips
- Wrong-password and tamper detection
- Vault upload/download workflow
- S3 integration through LocalStack
- FastAPI upload, download, list, and error responses

## Project Structure

```text
s3-crypt-vault/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── crypto/
│   │   ├── envelope.py
│   │   └── kdf.py
│   ├── cli.py
│   ├── config.py
│   ├── exceptions.py
│   ├── s3_client.py
│   └── vault.py
├── tests/
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Interview Talking Points

- The system uses client-side encryption so plaintext is never stored in S3.
- FastAPI handles HTTP concerns, while `CryptVault` contains the backend workflow.
- `S3Client` isolates boto3 calls from the rest of the application.
- Envelope encryption gives each file its own random data encryption key.
- `scrypt` turns a human password into a cryptographic key.
- AES-GCM detects wrong passwords and tampered ciphertext.
- The project does not protect against weak passwords, compromised machines, or lost passwords.

## License

This project is licensed under the MIT License.
