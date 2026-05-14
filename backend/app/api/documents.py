from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
import os
import uuid

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import save_document_meta, list_documents, get_document
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/documents", tags=["文档"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
        "text/csv",
        "image/png",
        "image/jpeg",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

    file_ext = file.filename.split(".")[-1] if file.filename else "bin"
    object_name = f"{uuid.uuid4().hex}.{file_ext}"

    content = await file.read()

    save_dir = os.path.join(settings.upload_dir, str(current_user.id))
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, object_name)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    doc = await save_document_meta(
        db,
        filename=file.filename or "unknown",
        file_size=len(content),
        content_type=file.content_type or "application/octet-stream",
        file_path=file_path,
    )

    # TODO: 异步调用 MinerU 解析 + 向量化
    # await parse_and_index.delay(doc.id)

    return DocumentUploadResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        message="文档上传成功，正在解析中...",
    )


@router.get("", response_model=list[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_documents(db)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document_by_id(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc
