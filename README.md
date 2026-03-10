# S3 Crypt Vault

A Python-based CLI tool for client-side encrypted AWS S3 storage.

## Project Overview

This project demonstrates a Zero-Knowledge architecture. Files are encrypted locally using AES-256 before being transmitted to AWS S3. Even if the S3 bucket is compromised, the data remains unreadable without the local master key.

## Security Features

- Client-Side Encryption: Implementation of the cryptography library for robust data protection.
- Secure Credential Management: No hardcoded secrets. Uses environment variables and AWS IAM roles.
- Integrity Checks: Ensuring data hasn't been tampered with during transit.

## Installation & Usage

1. `pip install -r requirements.txt`
2. Configure your `.env` with `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
3. Run: `python -m app.main upload ./my_document.pdf`