from fastapi import APIRouter, Depends

from app.api.dependencies import get_vault
from app.api.schemas import FileListResponse
from app.vault import CryptVault


router = APIRouter()


@router.get("/files", response_model=FileListResponse)
def list_files(vault: CryptVault = Depends(get_vault)):
    files = vault.s3.list_objects()
    return FileListResponse(files=files)