# repositories/stored_file_repository.py
from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.model import StoredFile, StoredFileBlob, StoredFileStatus


class StoredFileRepository:
    def __init__(self, session: Session):
        self.session = session

    # -------- Read --------
    def get_meta(self, file_id: uuid.UUID) -> Optional[StoredFile]:
        stmt = select(StoredFile).where(
            StoredFile.id == file_id,
            StoredFile.is_deleted == False,
        )
        return self.session.execute(stmt).scalars().first()

    def list_meta(
        self,
        *,
        user_id: str | None = None,
        status: StoredFileStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[StoredFile]:
        stmt = select(StoredFile).where(StoredFile.is_deleted == False)

        if user_id is not None:
            stmt = stmt.where(StoredFile.user_id == user_id)
        if status is not None:
            stmt = stmt.where(StoredFile.status == status)

        stmt = stmt.order_by(StoredFile.created_at.desc()).limit(limit).offset(offset)
        return self.session.execute(stmt).scalars().all()

    def get_blob_b64(self, file_id: uuid.UUID) -> Optional[str]:
        stmt = select(StoredFileBlob.content_b64).where(StoredFileBlob.file_id == file_id)
        return self.session.execute(stmt).scalars().first()

    def find_by_user_and_sha256(self, user_id: str, sha256_hex: str) -> Optional[StoredFile]:
        stmt = select(StoredFile).where(
            StoredFile.user_id == user_id,
            StoredFile.sha256_hex == sha256_hex,
            StoredFile.is_deleted == False,
        )
        return self.session.execute(stmt).scalars().first()

    # -------- Create (dedup-safe) --------
    def create_with_blob_dedup_safe(
        self,
        *,
        user_id: str | None,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        sha256_hex: str,
        content_b64: str,
    ) -> tuple[StoredFile, bool]:
        """
        返回 (obj, deduplicated)
        并发安全：DB 唯一约束 uq_stored_files_user_sha256 兜底。
        """
        if user_id is not None:
            existing = self.find_by_user_and_sha256(user_id, sha256_hex)
            if existing:
                return existing, True

        obj = StoredFile(
            user_id=user_id,
            original_filename=original_filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            sha256_hex=sha256_hex,
            status=StoredFileStatus.UPLOADED,
            is_deleted=False,
        )
        blob = StoredFileBlob(content_b64=content_b64)
        obj.blob = blob

        self.session.add(obj)

        try:
            # flush 触发 insert，能尽早发现唯一约束冲突
            self.session.flush()
        except IntegrityError:
            # 并发竞态：另一请求先插入成功
            self.session.rollback()  # 注意：repo 层 rollback 只为修复当前 flush 的失败态
            if user_id is None:
                # 没有 user_id 就无法按 uq 去重，直接抛出
                raise
            existing = self.find_by_user_and_sha256(user_id, sha256_hex)
            if existing:
                return existing, True
            raise

        self.session.refresh(obj)
        return obj, False

    # -------- Update --------
    def update_status(
        self,
        file_id: uuid.UUID,
        *,
        status: StoredFileStatus,
        error_message: str | None = None,
    ) -> Optional[StoredFile]:
        obj = self.get_meta(file_id)
        if not obj:
            return None
        obj.status = status
        obj.error_message = error_message
        self.session.flush()
        self.session.refresh(obj)
        return obj

    # -------- Delete (soft) --------
    def soft_delete(self, file_id: uuid.UUID) -> bool:
        obj = self.get_meta(file_id)
        if not obj:
            return False
        obj.is_deleted = True
        obj.status = StoredFileStatus.DELETED
        self.session.flush()
        return True