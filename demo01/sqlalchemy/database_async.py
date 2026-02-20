# database_async.py
from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .settings import settings  # 按你项目实际 import
import logging

logger = logging.getLogger(__name__)


def create_database_url() -> URL:
    # 复用你现有的 URL.create 写法
    return URL.create(
        drivername="postgresql+psycopg",  # 你现状就是这个（psycopg3）
        username=settings.PG_USER,
        password=settings.PG_PASSWORD,
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        database=settings.PG_DB,
    )


def create_async_engine_and_session(url: str | URL) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    try:
        engine = create_async_engine(
            url,
            echo=settings.DATABASE_ECHO,
            echo_pool=settings.DATABASE_POOL_ECHO,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            # schema_translate_map 你同步里用了，这里也保持一致
            execution_options={"schema_translate_map": {None: settings.PG_SCHEMA}},
        )
    except Exception:
        logger.exception("Async Database 接续失败。")
        raise

    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return engine, session_factory


# FastAPI dependency
async def get_async_db(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
        finally:
            # async with 会自动 close
            pass
