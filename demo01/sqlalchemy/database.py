# components/database.py (sync)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import URL

def create_database_url(settings) -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.PG_USER,
        password=settings.PG_PASSWORD,
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        database=settings.PG_DB,
    )

def create_engine_and_sessionmaker(url: str | URL, settings):
    engine = create_engine(
        url,
        echo=settings.DATABASE_ECHO,
        echo_pool=settings.DATABASE_POOL_ECHO,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        execution_options={"schema_translate_map": {None: settings.PG_SCHEMA}},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return engine, SessionLocal
