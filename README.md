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

### Upload Flow

```text
User uploads file + password
  -> FastAPI receives multipart request
  -> CryptVault reads file bytes
  -> scrypt derives a key from the password
  -> A random data encryption key encrypts the file
  -> The data encryption key is encrypted with the password-derived key
  -> S3Client uploads the encrypted SCV2 blob to S3
```

### Download Flow

```text
User requests object + password
  -> FastAPI receives download request
  -> S3Client downloads encrypted bytes from S3
  -> CryptVault parses the SCV2 blob
  -> scrypt derives the key from the password and stored salt
  -> The data encryption key is decrypted
  -> The file content is decrypted and returned to the user
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

## Security Model

This project uses client-side encryption. The application encrypts data before upload, and S3 only stores encrypted blobs.

### Protects Against

- Someone reading raw objects directly from the S3 bucket.
- Accidental exposure of encrypted files in cloud storage.
- Tampering with encrypted file contents, because AES-GCM detects modification.

### Does Not Protect Against

- Weak or reused passwords.
- A compromised machine running the API or CLI.
- A malicious user who already has the correct password.
- Loss of the password. There is no recovery mechanism.
- Full production compliance requirements such as centralized key rotation, audit trails, or access governance.

## Limitations

- Files are processed in memory, so very large file uploads are not ideal.
- Passwords are supplied per upload/download request and are not managed by a dedicated secret manager.
- There is no user authentication or authorization layer.
- There is no database for metadata, ownership, sharing, or access history.
- Object keys are based on filenames, so duplicate names are rejected instead of versioned.
- The project focuses on backend architecture and encryption flow, not production-grade identity or compliance.

## Trade-Offs

- Password-based encryption keeps the project simple and easy to run locally, but production systems usually centralize key management.
- Client-side encryption means S3 never sees plaintext, but the API must handle passwords carefully during each request.
- LocalStack makes S3 integration testable without AWS costs, but it is still an emulator.
- Keeping the app stateless makes the backend easier to understand, but limits features like file ownership, audit logs, and sharing.
- Envelope encryption is more complex than encrypting directly with one key, but it better models real-world encrypted storage systems.

## How I Would Redesign This In Production

If I redesigned this for production, I would keep the same high-level idea but change the operational security model:

- Use AWS KMS to manage master keys instead of deriving all key-encryption keys from user passwords.
- Use IAM roles instead of static AWS access keys in `.env`.
- Add key rotation so encrypted data can be re-wrapped with newer KMS keys over time.
- Add audit logs for upload, download, failed decryption attempts, and administrative actions.
- Add authentication and authorization so users can only access their own objects.
- Store metadata in a database, including owner, object key, content type, creation time, and key version.
- Stream large files instead of reading entire files into memory.
- Add rate limiting and stronger validation around filenames and object keys.

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
|-- app/
|   |-- api/
|   |   |-- dependencies.py
|   |   |-- exceptions.py
|   |   |-- main.py
|   |   |-- routes.py
|   |   `-- schemas.py
|   |-- crypto/
|   |   |-- envelope.py
|   |   `-- kdf.py
|   |-- cli.py
|   |-- config.py
|   |-- exceptions.py
|   |-- s3_client.py
|   `-- vault.py
|-- tests/
|-- docker-compose.yml
|-- pyproject.toml
`-- README.md
```

## Interview Talking Points

- The system uses client-side encryption so plaintext is never stored in S3.
- FastAPI handles HTTP concerns, while `CryptVault` contains the backend workflow.
- `S3Client` isolates boto3 calls from the rest of the application.
- Envelope encryption gives each file its own random data encryption key.
- `scrypt` turns a human password into a cryptographic key.
- AES-GCM detects wrong passwords and tampered ciphertext.
- The project clearly separates learning-project limitations from production concerns.

## License

This project is licensed under the MIT License.
