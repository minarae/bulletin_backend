from typing import Generator

from app.db.session import SessionLocal


def get_db() -> Generator:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
