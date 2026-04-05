from fastapi import FastAPI

from app.api.exceptions import (
    password_required_handler,
    decryption_error_handler,
    storage_error_handler,
    generic_error_handler,
)
from app.exceptions import PasswordRequiredError, DecryptionError, StorageError


app = FastAPI(title="S3 Crypt Vault API")

app.add_exception_handler(PasswordRequiredError, password_required_handler)
app.add_exception_handler(DecryptionError, decryption_error_handler)
app.add_exception_handler(StorageError, storage_error_handler)
app.add_exception_handler(Exception, generic_error_handler)


@app.get("/health")
def health():
    return {"status": "ok"}
