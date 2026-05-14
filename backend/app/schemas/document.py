from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    content_type: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str
