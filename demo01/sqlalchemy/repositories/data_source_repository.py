# repositories/data_source_repository.py
from typing import List
from sqlalchemy.orm import Session
from xxxx.model.prompt_model import DataSource

class DataSourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def select(self) -> List[DataSource]:
        return (
            self.session.query(DataSource)
            .filter(DataSource.is_deleted == False)
            .all()
        )

    def select_by_ids(self, ids: List[int]) -> List[DataSource]:
        return (
            self.session.query(DataSource)
            .filter(DataSource.id.in_(ids), DataSource.is_deleted == False)
            .all()
        )
