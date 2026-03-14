# S3 Crypt Vault

A Python-based CLI tool for client-side encrypted AWS S3 storage.

## Project Overview

This project demonstrates a **Zero-Knowledge architecture**. Files are encrypted locally using **AES-256 GCM** before being transmitted to AWS S3. Even if the S3 bucket is compromised, the data remains unreadable without the local master key. This ensures that the Cloud provider never sees the plaintext data.

## Security Features

* **Client-Side Encryption:** Uses the `cryptography` library (AES-GCM) to ensure both confidentiality and data integrity.
* **Zero-Knowledge:** The encryption key is generated and stored locally; it never leaves the user's environment.
* **Secure Credential Management:** No hardcoded secrets. It fully supports environment variables and follows AWS security best practices.
* **Local Emulation:** Integrated with **LocalStack** for secure, cost-free local development and testing.

## Technical Stack & CI/CD

* **Language:** Python 3.14+
* **Cloud Provider:** AWS (S3)
* **Infrastructure Emulation:** LocalStack & Docker Compose
* **Automation:** GitHub Actions (CI) for automated linting and integration testing.

## Installation & Usage

1. **Clone the repository:**
```bash
git clone https://github.com/michaelgiuliano/s3-crypt-vault.git
cd s3-crypt-vault
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Local Development (LocalStack):**
Start the local S3 environment:
```bash
docker-compose up -d
```

4. **Environment Setup:**
Create a `.env` file based on `.env.example`:
```text
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=eu-north-1
USE_LOCALSTACK=true
```

5. **Run Tests:**
```bash
pytest tests/
```

## Encryption Architecture

All files are encrypted locally before being uploaded to AWS S3.

The project uses **AES-256-GCM**, an authenticated encryption mode that ensures:

- **Confidentiality** – data cannot be read without the key
- **Integrity** – tampering with ciphertext is detected
- **Authenticity** – decryption fails if data is modified

### Encryption Flow

1. File is read locally
2. A random 12-byte nonce is generated
3. AES-256-GCM encrypts the file
4. The nonce is prepended to the ciphertext
5. The encrypted file is uploaded to S3

### Tamper Detection

AES-GCM provides built-in authentication.  
If even a single bit of ciphertext is modified, decryption will raise an error.

This behavior is verified by `test_tamper_detection()`.