# services/file_download_service.py
from __future__ import annotations

import base64
import binascii
import uuid
from typing import Iterator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..repositories.stored_file_repository import StoredFileRepository


class FileDownloadService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StoredFileRepository(db)

    def get_meta(self, file_id: uuid.UUID):
        obj = self.repo.get_meta(file_id)
        if not obj:
            raise HTTPException(status_code=404, detail="File not found")
        return obj

    def get_base64(self, file_id: uuid.UUID) -> tuple[object, str]:
        res = self.repo.get_meta_and_blob(file_id)
        if not res:
            raise HTTPException(status_code=404, detail="File not found")
        return res

    def iter_decoded_bytes(self, b64: str, *, chunk_chars: int = 4 * 1024 * 1024) -> Iterator[bytes]:
        """
        将 base64 TEXT 流式解码为 bytes 迭代器。
        - base64 必须按 4 字符对齐；这里会处理边界 remainder。
        - chunk_chars 是“字符数”，不是字节数。
        """
        remainder = ""
        n = len(b64)

        # 逐段处理，避免一次性 b64decode 全量占内存
        for i in range(0, n, chunk_chars):
            part = remainder + b64[i : i + chunk_chars]
            cut = (len(part) // 4) * 4
            to_decode, remainder = part[:cut], part[cut:]
            if to_decode:
                try:
                    yield base64.b64decode(to_decode, validate=False)
                except (binascii.Error, ValueError):
                    raise HTTPException(status_code=500, detail="Corrupted base64 data")

        if remainder:
            try:
                yield base64.b64decode(remainder, validate=False)
            except (binascii.Error, ValueError):
                raise HTTPException(status_code=500, detail="Corrupted base64 data")