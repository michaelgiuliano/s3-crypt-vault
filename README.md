# S3 Crypt Vault
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/michaelgiuliano/s3-crypt-vault/actions/workflows/ci.yml/badge.svg)

>A secure client-side encrypted storage system for AWS S3.


## Project Overview

This project implements a **secure storage system** based on client-side encryption and zero-knowledge principles.

Files are encrypted locally using **AES-256-GCM** with an envelope encryption model before being transmitted to AWS S3. Even if the S3 bucket is compromised, the stored data remains unreadable without the local encryption key.

The cloud provider never has access to plaintext data, ensuring that encryption and decryption always occur on the client side.


## Architecture

The system is composed of multiple layers, each with a clear responsibility:

- **CLI Layer (Typer)**  
  Handles user interaction and command execution.

- **Vault Layer (`CryptVault`)**  
  Orchestrates encryption and storage operations.

- **Encryption Layer**  
  Implements client-side encryption using AES-256-GCM and envelope encryption.

- **Storage Layer (`S3Client`)**  
  Handles communication with AWS S3 (or LocalStack in development).

- **Error Handling Layer**  
  Provides domain-specific exceptions to ensure consistent error propagation across components.

### Data Flow

```
User Input
 ↓
CLI (commands)
 ↓
Vault (orchestration)
 ↓
Encryption (client-side)
 ↓
S3 Client
 ↓
AWS S3
```

This separation ensures that encryption always happens locally before any data is transmitted to the cloud.


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

- **Client-side encryption** using *AES-256-GCM* with envelope encryption and password-based key derivation (`scrypt`).
- **Zero-knowledge design** – the encryption key never leaves the local environment.
- Secure **AWS integration** using environment-based credentials.
- Local development support with **LocalStack**.
- Installable CLI tool (**`s3vault`**) for interacting with encrypted storage.
- **Integration testing** using *pytest*.
- **CI pipeline** with GitHub Actions.


## Technical Stack

- **Language**: Python 3.12+
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

### Dependency Management

This project uses `pip-tools` for reproducible dependency management.

To update dependencies:

```bash
pip-compile requirements.in
pip-compile dev-requirements.in
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
> Note: Upload and download operations require a password for encryption/decryption (v2 format).

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

### v2 Encryption Model (Envelope Encryption)

Starting from version 0.2.0, the vault uses an envelope encryption scheme:

- A **Data Encryption Key (DEK)** is generated per file
- A **master key** is derived from a user password using scrypt
- The file is encrypted with the DEK (AES-256-GCM)
- The DEK is encrypted with the master key

This improves:

- Key isolation per file
- Reduced blast radius in case of compromise
- No persistent master key stored on disk

### Encryption Flow

```
File is read locally
        ↓
A random 12-byte nonce is generated
        ↓
AES-256-GCM encrypts the file
        ↓
Encryption metadata is structured and stored alongside the ciphertext.
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
├───.github/
│   └───workflows/
│       └───ci.yml
├───app/
│   ├───crypto/
│   │   ├───__init__.py
│   │   ├───envelope.py
│   │   └───kdf.py
│   ├───__init__.py
│   ├───cli.py
│   ├───config.py
│   ├───encryptor.py
│   ├───exceptions.py
│   ├───s3_client.py
│   └───vault.py
├───tests/
│   ├───__init__.py
│   ├───test_encryption.py
│   ├───test_s3_client.py
│   ├───test_s3_connection.py
│   └───test_vault.py
├───.env.example
├───.gitignore
├───CHANGELOG.md
├───dev-requirements.in
├───dev-requirements.txt
├───docker-compose.yml
├───LICENSE
├───pyproject.toml
├───README.md
├───requirements.in
└───requirements.txt
```

## License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software with proper attribution. See the LICENSE file for the full license text.