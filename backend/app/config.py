import secrets
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache
from pathlib import Path

# 项目根目录: config.py -> app -> backend -> fintech-brain
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # LLM
    judge_model_name: str = "gpt-4"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"

    # SiliconFlow (Embedding + Reranker)
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"

    # Embedding
    embedding_model: str = "BAAI/bge-large-zh-v1.5"

    # Reranker
    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    # MinerU API (optional, falls back to local magic-pdf if empty)
    mineru_api_key: str = ""

    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "finance_brain"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # CORS
    cors_origins: str = "http://localhost,http://localhost:80,http://localhost:3000,http://localhost:5173"

    # File Storage
    upload_dir: str = "uploads"

    # JWT
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    @model_validator(mode="after")
    def validate_security_defaults(self) -> "Settings":
        if not self.jwt_secret_key:
            self.jwt_secret_key = secrets.token_urlsafe(48)
        return self

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def sync_mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
