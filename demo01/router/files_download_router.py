from __future__ import annotations

import mimetypes
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from ..deps import get_db
from ..services.file_download_service import FileDownloadService

router = APIRouter(prefix="/v1/files", tags=["files"])

import re
from urllib.parse import quote

def _ascii_fallback(name: str) -> str:
    # 去掉控制字符、引号等；并把非 ASCII 替换为下划线
    name = re.sub(r'[\r\n"]', "_", name)
    return name.encode("ascii", "ignore").decode("ascii") or "download"

def build_content_disposition(filename: str) -> str:
    fallback = _ascii_fallback(filename)
    quoted = quote(filename, safe="")  # UTF-8 percent-encoding
    # RFC 5987
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quoted}"

@router.get("/{file_id}/download", summary="Download file as binary stream (recommended)")
def download_file(file_id: uuid.UUID, db: Session = Depends(get_db)):
    svc = FileDownloadService(db)
    file_obj, b64 = svc.get_base64(file_id)

    filename = file_obj.original_filename
    cd = build_content_disposition(file_obj.original_filename)
    media_type = file_obj.mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    # StreamingResponse：边解码边返回，内存稳定
    return StreamingResponse(
        svc.iter_decoded_bytes(b64),
        media_type=media_type,
        headers={
            # attachment 触发下载；filename 建议做更严格的清洗/编码（生产可再加强）
            "Content-Disposition": cd'
        },
    )


@router.get("/{file_id}/download-base64", summary="Download file as base64 (for debug / client-side decode)")
def download_file_base64(file_id: uuid.UUID, db: Session = Depends(get_db)):
    svc = FileDownloadService(db)
    file_obj, b64 = svc.get_base64(file_id)

    return JSONResponse(
        {
            "id": str(file_obj.id),
            "original_filename": file_obj.original_filename,
            "mime_type": file_obj.mime_type,
            "size_bytes": file_obj.size_bytes,
            "sha256": file_obj.sha256_hex,
            "content_b64": b64,
        }
    )