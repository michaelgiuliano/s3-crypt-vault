from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import PasswordRequiredError, DecryptionError, StorageError


async def password_required_handler(request: Request, exc: PasswordRequiredError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def decryption_error_handler(request: Request, exc: DecryptionError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def storage_error_handler(request: Request, exc: StorageError):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)},
    )


async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )