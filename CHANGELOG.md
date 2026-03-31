# Changelog


## v0.2.2 - Core Refactor & API Readiness

- Decoupled configuration from global state
- Separated core logic from I/O concerns
- Removed interactive input from core logic
- Introduced domain-specific exceptions
- Improved test coverage


## v0.2.1 - Hardening & Production Readiness

- Added fail-fast environment configuration validation
- Improved S3 client with explicit error handling
- Secured password input (no terminal echo)
- Introduced reproducible dependency management (pip-tools)
- Updated documentation (architecture + positioning)
- Aligned Python version (`>=3.12`) and CI environment


## v0.2.0 - Envelope Encryption & Structured Format

- Introduced envelope encryption model using per-file DEK and password-derived master key (scrypt)
- Implemented structured binary format (SCV2) with versioned header
- Added authenticated encryption (AES-256-GCM) with AAD binding (magic + version)
- Improved parsing robustness with explicit format validation
- Added backward compatibility for legacy v1 encrypted files
- Refactored vault to use envelope encryption (v2) as default


## v0.1.1 - Repository Improvements

- Improved README with detailed security model explanation
- Added CHANGELOG for version tracking
- Enhanced repository metadata (description, topics, badges)
- General documentation and formatting improvements


## v0.1.0 - Initial Release

- AES-256-GCM client-side encryption
- Zero-knowledge storage model
- CLI tool (s3vault)
- AWS S3 integration
- LocalStack support
- Pytest test suite
- GitHub Actions CI