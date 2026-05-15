import asyncio
import io
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import httpx

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

MINERU_API_BASE = "https://mineru.net/api/v4"
POLL_INTERVAL = 3  # seconds
POLL_TIMEOUT = 300  # seconds


# ─── MinerU API mode ───────────────────────────────────────────

async def _upload_to_temp_host(file_path: str) -> str:
    """Upload local file to filebin.net, return public URL."""
    if not os.path.isabs(file_path):
        file_path = os.path.join("/app", file_path)

    filename = Path(file_path).name
    async with httpx.AsyncClient(timeout=120) as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                "https://filebin.net",
                headers={"filename": filename, "Accept": "application/json"},
                content=f.read(),
            )
        resp.raise_for_status()
        data = resp.json()
        bin_id = data["bin"]["id"]
        url = f"https://filebin.net/{bin_id}/{filename}"
        logger.info(f"File uploaded to filebin: {url}")
        return url


async def _parse_via_api(file_path: str) -> dict:
    """Parse document using MinerU cloud API."""
    api_key = settings.mineru_api_key
    headers = {"Authorization": f"Bearer {api_key}"}

    # Step 1: Upload file to get a public URL
    file_url = await _upload_to_temp_host(file_path)

    # Step 2: Create extraction task
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{MINERU_API_BASE}/extract/task",
            headers=headers,
            json={
                "url": file_url,
                "is_ocr": True,
                "enable_formula": True,
                "enable_table": True,
                "language": "ch",
            },
        )
        resp.raise_for_status()
        result = resp.json()

    if result.get("code") != 0:
        raise RuntimeError(f"MinerU API error: {result.get('msg')}")

    task_id = result["data"]["task_id"]
    logger.info(f"MinerU task created: {task_id}")

    # Step 3: Poll for completion
    async with httpx.AsyncClient(timeout=30) as client:
        elapsed = 0
        while elapsed < POLL_TIMEOUT:
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

            resp = await client.get(
                f"{MINERU_API_BASE}/extract/task/{task_id}",
                headers=headers,
            )
            resp.raise_for_status()
            status = resp.json()

            if status.get("code") != 0:
                raise RuntimeError(f"MinerU poll error: {status.get('msg')}")

            state = status["data"].get("state", "")
            if state == "done":
                zip_url = status["data"]["full_zip_url"]
                logger.info(f"MinerU task done, downloading result: {zip_url}")
                return await _download_and_extract_zip(zip_url)
            elif state == "failed":
                raise RuntimeError(f"MinerU task failed: {status['data'].get('err_msg')}")

        raise RuntimeError(f"MinerU task timeout after {POLL_TIMEOUT}s")


async def _download_and_extract_zip(zip_url: str) -> dict:
    """Download MinerU result zip and extract markdown content."""
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.get(zip_url)
        resp.raise_for_status()

    markdown_content = ""
    content_list = []

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for name in zf.namelist():
            if name.endswith(".md"):
                markdown_content = zf.read(name).decode("utf-8")
            elif name.endswith("_content_list.json"):
                content_list = json.loads(zf.read(name).decode("utf-8"))

    return {
        "content_list": content_list,
        "markdown": markdown_content,
    }


# ─── Local magic-pdf mode ──────────────────────────────────────

async def _parse_via_local(file_path: str, output_dir: str) -> dict:
    """Parse document using local magic-pdf CLI."""
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "magic-pdf",
        "-p", file_path,
        "-o", output_dir,
        "-m", "auto",
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        if proc.returncode != 0:
            err_msg = stderr.decode("utf-8", errors="replace")
            logger.error(f"MinerU failed: {err_msg}")
            raise RuntimeError(f"文档解析失败: {err_msg}")
        logger.info(f"MinerU parsed: {file_path}")
    except asyncio.TimeoutError:
        logger.error(f"MinerU timeout: {file_path}")
        raise RuntimeError("文档解析超时（300秒）")

    stem = Path(file_path).stem
    output_file = Path(output_dir) / f"{stem}_content_list.json"
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            content_list = json.load(f)
    else:
        content_list = []

    md_file = Path(output_dir) / f"{stem}.md"
    markdown_content = ""
    if md_file.exists():
        markdown_content = md_file.read_text(encoding="utf-8")

    # Cleanup temp output
    try:
        shutil.rmtree(output_dir, ignore_errors=True)
    except Exception:
        pass

    return {
        "content_list": content_list,
        "markdown": markdown_content,
    }


# ─── Public entry point ────────────────────────────────────────

async def parse_document(file_path: str, output_dir: str = "/tmp/mineru_output") -> dict:
    """Parse document using MinerU API (if configured) or local magic-pdf."""
    if settings.mineru_api_key:
        for attempt in range(3):
            try:
                logger.info(f"Using MinerU API for: {file_path} (attempt {attempt + 1})")
                return await _parse_via_api(file_path)
            except Exception as e:
                logger.warning(f"MinerU API attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)

    logger.info(f"Using local magic-pdf for: {file_path}")
    return await _parse_via_local(file_path, output_dir)


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
