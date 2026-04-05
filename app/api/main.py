from fastapi import FastAPI

from app.api.exceptions import (
    password_required_handler,
    decryption_error_handler,
    storage_error_handler,
    file_not_found_handler,
    generic_error_handler,
)
from app.api.routes import router
from app.exceptions import PasswordRequiredError, DecryptionError, StorageError


app = FastAPI(title="S3 Crypt Vault API", version="0.3.0")

app.add_exception_handler(PasswordRequiredError, password_required_handler)
app.add_exception_handler(DecryptionError, decryption_error_handler)
app.add_exception_handler(StorageError, storage_error_handler)
app.add_exception_handler(Exception, generic_error_handler)
app.add_exception_handler(FileNotFoundError, file_not_found_handler)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
