from fastapi import Request, HTTPException
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

async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

async def generic_error_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )