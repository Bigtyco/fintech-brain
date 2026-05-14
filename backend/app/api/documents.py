from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
import asyncio
import os
import uuid

from app.core.database import get_db, async_session
from app.core.logging import logger
from app.deps import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import save_document_meta, list_documents, get_document, update_document_status, update_document_content
from app.parser.mineru_parser import parse_document, chunk_text
from app.rag.embeddings import get_embeddings
from app.rag.milvus_client import insert_vectors
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/documents", tags=["文档"])


async def parse_and_index_document(doc_id: int, file_path: str):
    """后台任务：解析文档并写入向量库（使用独立数据库会话）"""
    async with async_session() as db:
        try:
            logger.info(f"Starting document parsing: doc_id={doc_id}")
            await update_document_status(db, doc_id, "parsing")
            await db.commit()

            # 解析文档
            result = await parse_document(file_path)
            markdown_content = result.get("markdown", "")

            if not markdown_content:
                logger.warning(f"No content extracted from document: doc_id={doc_id}")
                await update_document_status(db, doc_id, "completed", chunk_count=0)
                await db.commit()
                return

            # 文本分块
            chunks = chunk_text(markdown_content)
            logger.info(f"Document chunked: doc_id={doc_id}, chunks={len(chunks)}")

            # 获取向量
            texts = [c["content"] for c in chunks]
            embeddings = await get_embeddings(texts)
            logger.info(f"Embeddings generated: doc_id={doc_id}, count={len(embeddings)}")

            # 写入 Milvus
            insert_vectors(doc_id, chunks, embeddings)
            logger.info(f"Vectors inserted to Milvus: doc_id={doc_id}")

            # 更新状态和解析内容
            await update_document_status(db, doc_id, "completed", chunk_count=len(chunks))
            await update_document_content(db, doc_id, markdown_content[:10000])
            await db.commit()

            logger.info(f"Document processing completed: doc_id={doc_id}")

        except Exception as e:
            logger.error(f"Document processing failed: doc_id={doc_id}, error={e}")
            await db.rollback()
            try:
                await update_document_status(db, doc_id, "failed", error=str(e))
                await db.commit()
            except Exception:
                pass


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

    # 异步调用解析和向量化（不传递 db，后台任务会创建独立会话）
    asyncio.create_task(parse_and_index_document(doc.id, file_path))

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
