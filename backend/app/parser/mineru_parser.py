import subprocess
import json
import os
from pathlib import Path
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


async def parse_document(file_path: str, output_dir: str = "/tmp/mineru_output") -> dict:
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "magic-pdf",
        "-p", file_path,
        "-o", output_dir,
        "-m", "auto",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
        logger.info(f"MinerU parsed: {file_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"MinerU failed: {e.stderr}")
        raise RuntimeError(f"文档解析失败: {e.stderr}")

    output_file = Path(output_dir) / f"{Path(file_path).stem}_content_list.json"
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            content_list = json.load(f)
    else:
        content_list = []

    md_file = Path(output_dir) / f"{Path(file_path).stem}.md"
    markdown_content = ""
    if md_file.exists():
        markdown_content = md_file.read_text(encoding="utf-8")

    return {
        "content_list": content_list,
        "markdown": markdown_content,
        "output_dir": str(output_dir),
    }


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[dict]:
    if len(text) <= chunk_size:
        return [{"content": text, "metadata": {"chunk_index": 0}}]

    chunks = []
    start = 0
    index = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({
            "content": chunk,
            "metadata": {"chunk_index": index},
        })
        start = end - overlap
        index += 1

    return chunks
