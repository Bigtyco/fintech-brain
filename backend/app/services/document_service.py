import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.config import get_settings

settings = get_settings()


async def save_document_meta(
    db: AsyncSession, filename: str, file_size: int, content_type: str, file_path: str
) -> Document:
    doc = Document(
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        content_type=content_type,
        status="pending",
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def list_documents(db: AsyncSession) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


async def get_document(db: AsyncSession, doc_id: int) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    return result.scalar_one_or_none()


async def update_document_status(
    db: AsyncSession, doc_id: int, status: str, chunk_count: int = 0, error: str | None = None
):
    doc = await get_document(db, doc_id)
    if doc:
        doc.status = status
        doc.chunk_count = chunk_count
        if error:
            doc.error_message = error
        await db.flush()


async def update_document_content(
    db: AsyncSession, doc_id: int, parsed_content: str
):
    doc = await get_document(db, doc_id)
    if doc:
        doc.parsed_content = parsed_content
        await db.flush()
