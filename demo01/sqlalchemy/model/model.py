# model.py
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class StoredFileStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"         # 已上传（已入库）
    PROCESSING = "PROCESSING"     # 后续解析/入向量处理中
    READY = "READY"               # 可用于检索/对话
    FAILED = "FAILED"             # 处理失败
    DELETED = "DELETED"           # 逻辑删除


class StoredFile(Base):
    """
    元数据表：用于列表/检索/状态管理（不含大字段）
    """
    __tablename__ = "stored_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 多租户/用户隔离（没有就传 None）
    user_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # 原始文件信息
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # 去重与追踪
    sha256_hex: Mapped[str] = mapped_column(String(64), nullable=False)

    # 状态 & 可观测性字段
    status: Mapped[StoredFileStatus] = mapped_column(
        Enum(StoredFileStatus, name="stored_file_status"),
        nullable=False,
        default=StoredFileStatus.UPLOADED,
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # 逻辑删除
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    # 1:1 blob
    blob: Mapped["StoredFileBlob"] = relationship(
        back_populates="file",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        # 同一 user 下相同内容只存一份（并发安全：靠 DB 唯一约束兜底）
        UniqueConstraint("user_id", "sha256_hex", name="uq_stored_files_user_sha256"),
        Index("ix_stored_files_user_id", "user_id"),
        Index("ix_stored_files_sha256", "sha256_hex"),
        Index("ix_stored_files_status", "status"),
        Index("ix_stored_files_created_at", "created_at"),
        Index("ix_stored_files_is_deleted", "is_deleted"),
    )


class StoredFileBlob(Base):
    """
    大字段表：存 base64（避免 metadata 列表查询拖慢）
    """
    __tablename__ = "stored_file_blobs"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stored_files.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # 你要求 base64 存 PG -> TEXT
    content_b64: Mapped[str] = mapped_column(Text, nullable=False)

    # 可选：未来如果你要存“原始二进制”也可加一列 bytea
    # content_bytes: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    file: Mapped[StoredFile] = relationship(back_populates="blob", lazy="selectin")