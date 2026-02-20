from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.model import StoredFile, StoredFileStatus


class StoredFileRepoAsync:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_user_and_sha256(self, user_id: str, sha256_hex: str) -> Optional[StoredFile]:
        stmt = select(StoredFile).where(
            StoredFile.user_id == user_id,
            StoredFile.sha256_hex == sha256_hex,
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def create(
        self,
        *,
        user_id: str | None,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        sha256_hex: str,
        content_b64: str,
        status: StoredFileStatus = StoredFileStatus.UPLOADED,
    ) -> StoredFile:
        obj = StoredFile(
            user_id=user_id,
            original_filename=original_filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            sha256_hex=sha256_hex,
            content_b64=content_b64,
            status=status,
        )
        self.session.add(obj)
        # 注意：commit/rollback 建议放到 service 层统一管理（更企业级）
        await self.session.flush()     # 让 obj 拿到主键（如果是服务端生成）
        await self.session.refresh(obj)
        return obj

    async def mark_failed(self, file_id, reason: str | None = None) -> None:
        obj = await self.session.get(StoredFile, file_id)
        if not obj:
            return
        obj.status = StoredFileStatus.FAILED
        # 你也可以扩展一个 error_message 字段记录 reason
        await self.session.flush()
