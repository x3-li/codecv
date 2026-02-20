from fastapi import Depends
from sqlalchemy.orm import Session
from .deps import get_db
from .repositories.data_source_repository import DataSourceRepository

@router.get("/v1/data_sources")
def list_data_sources(db: Session = Depends(get_db)):
    repo = DataSourceRepository(db)
    return repo.select()

@router.post("/v1/files")
async def upload_file(..., db: AsyncSession = Depends(get_async_db)):
    ...
