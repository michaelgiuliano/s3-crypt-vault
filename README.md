# S3 Crypt Vault
![Python](https://img.shields.io/badge/python-3.14-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/michaelgiuliano/s3-crypt-vault/actions/workflows/ci.yml/badge.svg)

>A Python CLI tool for **zero-knowledge encrypted storage on AWS S3**.


## Project Overview

This project demonstrates a **Zero-Knowledge architecture for cloud storage**.

Files are encrypted locally using **AES-256-GCM** before being transmitted to AWS S3. Even if the S3 bucket is compromised, the stored data remains unreadable without the local encryption key.

The cloud provider never has access to plaintext data, ensuring that encryption and decryption always occur on the client side.


## Security Model

This project follows a zero-knowledge architecture:

### What it protects against

- Compromise of the S3 bucket
- Unauthorized access to stored objects
- Data leakage from cloud provider

### What it does NOT protect against

- Loss or theft of the encryption key
- Compromise of the local machine
- Weak user key management practices

### Key Responsibility

The user is fully responsible for securely storing the encryption key.
If the key is lost, the data cannot be recovered.


## Features

- **Client-side encryption** using *AES-256-GCM*.
- **Zero-knowledge design** – the encryption key never leaves the local environment.
- Secure **AWS integration** using environment-based credentials.
- Local development support with **LocalStack**.
- Installable CLI tool (**`s3vault`**) for interacting with encrypted storage.
- **Integration testing** using *pytest*.
- **CI pipeline** with GitHub Actions.


## Technical Stack

- **Language**: Python 3.14+
- **Cloud Provider**: AWS S3
- **Infrastructure Emulation**: LocalStack + Docker Compose
- **Automation**: GitHub Actions (CI)
- **CLI Framework**: Typer
- **Testing**: Pytest


## Prerequisites

Before using the vault on AWS you must have:

- AWS credentials with S3 permissions
- An S3 bucket to store encrypted files

You can create one using the CLI:
```bash
s3vault create-bucket
```

Or via AWS CLI:
```bash
aws s3 mb s3://your-bucket-name
```

## Installation

Clone the repository:

```bash
git clone https://github.com/michaelgiuliano/s3-crypt-vault.git
cd s3-crypt-vault
```

Install the tool in editable mode:

```bash
pip install -e .
```

After installation the CLI command becomes available:

```bash
s3vault
```


## Environment Configuration

Create a `.env` file based on `.env.example`.

Example configuration:

```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=eu-north-1

S3_BUCKET_NAME=your-bucket-name-here

USE_LOCALSTACK=true
```

When `USE_LOCALSTACK=true`, the tool connects to a local S3 emulator instead of AWS.


## Local Development (LocalStack)

Start the local S3 environment:

```bash
docker-compose up -d
```

LocalStack allows the entire workflow to run locally without creating real AWS resources.


## CLI Usage

### Setup

```bash
# Generate a new encryption key:
s3vault init-key

# Create the configured S3 bucket:
s3vault create-bucket

# List available buckets:
s3vault list-buckets
```

### Operations

```bash
# Upload a file (encrypted locally before upload):
s3vault upload secret.txt

# List encrypted files stored in the configured bucket:
s3vault list-files

# Download and decrypt a file:
s3vault download secret.txt.enc decrypted.txt
```


## Encryption Architecture

All files are **encrypted locally** before being uploaded to S3.

The project uses **AES-256-GCM**, an authenticated encryption mode that ensures:

- **Confidentiality** – encrypted data cannot be read without the key
- **Integrity** – tampering with ciphertext is detected
- **Authenticity** – modified data cannot be successfully decrypted

### Encryption Flow

```
File is read locally
        ↓
A random 12-byte nonce is generated
        ↓
AES-256-GCM encrypts the file
        ↓
The nonce is prepended to the ciphertext
        ↓
The encrypted object is uploaded to S3
```

### Tamper Detection

*AES-GCM* provides **built-in authentication**.

If even a single bit of ciphertext is modified, decryption will fail with an authentication error.

This behavior is verified by the automated test `test_tamper_detection()`.

### Vault Workflow

The vault layer combines encryption and cloud storage.

Files follow this lifecycle:

```
file
 ↓
encrypt locally (AES-256-GCM)
 ↓
upload encrypted object to S3
 ↓
download encrypted object
 ↓
decrypt locally
```

This workflow is implemented in `app/vault.py` and verified by the end-to-end integration test `test_vault.py`.


## Testing

Run the full test suite:

```bash
pytest tests/
```

Tests cover:

- Encryption and decryption correctness
- Tamper detection
- S3 integration using LocalStack
- End-to-end vault workflow

## Continuous Integration

**GitHub Actions** automatically runs:

- Lint checks
- Integration tests
- LocalStack environment

On every `push` and `pull` request.


## Project Structure

```
s3-crypt-vault/
├───.github
│   └───workflows
│       └───ci.yml
├───app
│   ├───__init__.py
│   ├───cli.py
│   ├───config.py
│   ├───encryptor.py
│   ├───s3_client.py
│   └───vault.py
├───tests
│   ├───__init__.py
│   ├───test_encryption.py
│   ├───test_s3_client.py
│   ├───test_s3_connection.py
│   └───test_vault.py
├───.env.example
├───.gitignore
├───CHANGELOG.md
├───docker-compose.yml
├───LICENSE
├───pyproject.toml
├───README.md
└───requirements.txt
```

## License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software with proper attribution. See the LICENSE file for the full license text.