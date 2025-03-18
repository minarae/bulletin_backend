from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    CHAR,
    UniqueConstraint,
    Sequence,
    PrimaryKeyConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "tb_users"

    id = Column(Integer, Sequence("seq_users"), nullable=False, comment="사용자 ID")
    email = Column(String, unique=True, index=True, nullable=False, comment="이메일")
    hashed_password = Column(String, nullable=False, comment="비밀번호")
    full_name = Column(String, comment="이름")
    is_active = Column(Boolean(), default=True, comment="활성화 여부")
    is_superuser = Column(Boolean(), default=False, comment="슈퍼유저 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(1), nullable=False, default="F", comment="삭제 여부")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="삭제일시")

    # Relationships
    church_admin_roles = relationship("ChurchAdmin", back_populates="user")

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_users"),
        UniqueConstraint("email", name="uq_users__email"),
    )
