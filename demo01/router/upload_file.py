from __future__ import annotations

import base64
import hashlib
from typing import Final

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..deps import get_db
from ..services.file_upload_service import FileUploadService

router = APIRouter(prefix="/v1/files", tags=["files"])

# —— 可按 Gemini multimodal 需求与公司策略调整 ——
ALLOWED_MIME_TYPES: Final[set[str]] = {
    # images
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/heic",
    "image/heif",
    # documents
    "application/pdf",
    "text/plain",
}

MAX_UPLOAD_BYTES: Final[int] = 25 * 1024 * 1024  # 25MB（建议更保守，因为 base64 会膨胀约 33%）
CHUNK_SIZE: Final[int] = 1024 * 1024            # 1MB


def _read_and_base64_encode_sync(
    upload: UploadFile,
    *,
    max_bytes: int,
    chunk_size: int,
) -> tuple[str, str, int]:
    """
    同步分块读取（在 sync endpoint 线程池中执行，不阻塞 event loop）：
    - 限制大小
    - 计算 sha256
    - 流式 base64 编码（避免一次性读入内存）
    返回：(content_b64, sha256_hex, size_bytes)
    """
    sha = hashlib.sha256()
    total = 0

    remainder = b""
    parts: list[str] = []

    fileobj = upload.file  # SpooledTemporaryFile / file-like

    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break

        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max allowed is {max_bytes} bytes.",
            )

        sha.update(chunk)

        data = remainder + chunk
        cut = (len(data) // 3) * 3
        to_encode, remainder = data[:cut], data[cut:]

        if to_encode:
            parts.append(base64.b64encode(to_encode).decode("ascii"))

    if remainder:
        parts.append(base64.b64encode(remainder).decode("ascii"))

    return "".join(parts), sha.hexdigest(), total


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file/image for multimodal chat (stored as base64 in PostgreSQL)",
)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str | None = None,   # 你有认证体系的话建议从 token 里取，这里先留接口
    max_bytes: int = MAX_UPLOAD_BYTES,
):
    # 1) MIME 校验
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content_type={file.content_type}. Allowed: {sorted(ALLOWED_MIME_TYPES)}",
        )

    # 2) 文件名校验
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="filename is required")

    # 3) 读取 + base64 + sha256（分块）
    content_b64, sha256_hex, size_bytes = _read_and_base64_encode_sync(
        file, max_bytes=max_bytes, chunk_size=CHUNK_SIZE
    )

    # 4) 入库（repo 不 commit，service 负责事务）
    service = FileUploadService(db)
    obj, dedup = service.store_file(
        user_id=user_id,
        original_filename=filename,
        mime_type=file.content_type,
        size_bytes=size_bytes,
        sha256_hex=sha256_hex,
        content_b64=content_b64,
    )

    return {
        "id": str(obj.id),
        "deduplicated": dedup,
        "original_filename": obj.original_filename,
        "mime_type": obj.mime_type,
        "size_bytes": obj.size_bytes,
        "sha256": obj.sha256_hex,
        "status": obj.status,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }