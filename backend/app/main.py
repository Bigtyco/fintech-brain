from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.knowledge_graph.neo4j_client import neo4j_client
from app.api import auth, chat, documents, knowledge, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await neo4j_client.connect()
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
    allow_origins=["*"],
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
