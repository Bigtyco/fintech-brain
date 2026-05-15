from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.database import init_db
from app.core.logging import logger
from app.knowledge_graph.neo4j_client import neo4j_client
from app.rag.bm25 import bm25_index
from app.rag.milvus_client import load_all_documents
from app.api import auth, chat, documents, knowledge, dashboard

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await neo4j_client.connect()

    # Initialize BM25 index from existing documents in Milvus
    try:
        all_docs = load_all_documents()
        if all_docs:
            bm25_index.build_index(all_docs)
            logger.info(f"BM25 index initialized with {len(all_docs)} documents")
        else:
            logger.info("No existing documents for BM25 index")
    except Exception as e:
        logger.warning(f"BM25 index initialization skipped: {e}")

    yield
    await neo4j_client.close()


app = FastAPI(
    title="智能金融投研与风控大脑",
    description="基于 LangGraph 多 Agent 的金融投研与风控系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(knowledge.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
