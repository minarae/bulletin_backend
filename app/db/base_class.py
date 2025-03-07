from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """기본 모델 클래스"""

    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        """테이블 이름을 자동으로 생성"""
        return cls.__name__.lower()

    # 공통 컬럼이나 메서드를 여기에 추가할 수 있습니다.