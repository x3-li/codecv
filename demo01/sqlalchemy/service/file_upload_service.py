from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..repositories.stored_file_repository import StoredFileRepository
from ..models.model import StoredFile


class FileUploadService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StoredFileRepository(db)

    def store_file(
        self,
        *,
        user_id: str | None,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        sha256_hex: str,
        content_b64: str,
    ) -> tuple[StoredFile, bool]:
        try:
            obj, dedup = self.repo.create_with_blob_dedup_safe(
                user_id=user_id,
                original_filename=original_filename,
                mime_type=mime_type,
                size_bytes=size_bytes,
                sha256_hex=sha256_hex,
                content_b64=content_b64,
            )
            self.db.commit()
            return obj, dedup

        except IntegrityError as e:
            # 理论上 repo 已经兜底过一次，这里再兜底一次更稳（企业级防线）
            self.db.rollback()
            raise HTTPException(status_code=409, detail="Duplicate upload") from e

        except HTTPException:
            # 让上游 413/415/400 直接透传
            self.db.rollback()
            raise

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to store file") from e