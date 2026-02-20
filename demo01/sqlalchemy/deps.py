# deps.py (sync)
from fastapi import Request
from sqlalchemy.orm import Session

def get_db(request: Request):
    SessionLocal = request.app.state.db_session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
