# main.py (示意)
from fastapi import FastAPI

from .components.database import create_database_url, create_engine_and_session
from .components.database_async import create_async_engine_and_session

app = FastAPI()

@app.on_event("startup")
async def startup():
    url = create_database_url()

    # sync（旧模块继续用）
    engine, SessionLocal = create_engine_and_session(url)
    app.state.db_engine = engine
    app.state.db_session = SessionLocal

    # async（新上传模块用）
    async_engine, AsyncSessionLocal = create_async_engine_and_session(url)
    app.state.async_db_engine = async_engine
    app.state.async_db_session = AsyncSessionLocal


@app.on_event("shutdown")
async def shutdown():
    # sync engine dispose
    app.state.db_engine.dispose()
    # async engine dispose
    await app.state.async_db_engine.dispose()
