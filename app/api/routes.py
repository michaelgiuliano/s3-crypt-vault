from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.api.dependencies import get_vault
from app.api.schemas import FileListResponse, UploadResponse
from app.vault import CryptVault


router = APIRouter()


@router.get("/files", response_model=FileListResponse)
def list_files(vault: CryptVault = Depends(get_vault)):
    files = vault.s3.list_objects()
    return FileListResponse(files=files)


@router.post("/files", response_model=UploadResponse, status_code=201)
def upload_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    vault: CryptVault = Depends(get_vault),
):
    object_key = f"{file.filename}.enc"

    if vault.s3.object_exists(object_key):
        raise HTTPException(status_code=409, detail=f"File '{object_key}' already exists.")

    data = file.file.read()
    vault.upload_bytes(object_key, data, password)

    return UploadResponse(object_key=object_key)