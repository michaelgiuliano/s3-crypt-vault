from pydantic import BaseModel


class UploadResponse(BaseModel):
    object_key: str


class DownloadRequest(BaseModel):
    password: str


class FileListResponse(BaseModel):
    files: list[str]