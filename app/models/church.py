from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    CHAR,
    UniqueConstraint,
    Index,
    Sequence,
    ForeignKeyConstraint,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Church(Base):
    __tablename__ = "tb_churches"

    id = Column(Integer, Sequence("seq_churches"), nullable=False, comment="교회 ID")
    church_code = Column(String, unique=True, index=True, nullable=False, comment="교회 코드")
    name = Column(String, index=True, nullable=False, comment="교회 이름")
    address = Column(String, comment="교회 주소")
    contact_info = Column(String, comment="교회 연락처")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(1), nullable=False, default="F", comment="삭제 여부")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="삭제일시")

    # Relationships
    admins = relationship("ChurchAdmin", back_populates="church")
    bulletins = relationship("Bulletin", back_populates="church")
    templates = relationship("BulletinTemplate", back_populates="church")

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_churches"),
        UniqueConstraint("church_code", name="uq_churches__church_code"),
        Index("ix_churches__name", "name"),
    )


class ChurchAdmin(Base):
    __tablename__ = "tb_church_admins"

    id = Column(Integer, Sequence("seq_church_admins"), nullable=False, comment="교회 관리자 ID")
    church_id = Column(Integer, nullable=False, comment="교회 ID")
    user_id = Column(Integer, nullable=False, comment="사용자 ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(1), nullable=False, default="F", comment="삭제 여부")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="삭제일시")

    # Relationships
    church = relationship("Church", back_populates="admins")
    user = relationship("User", back_populates="church_admin_roles")

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_church_admins"),
        ForeignKeyConstraint(['church_id'], ['tb_churches.id'], name='fk_church_admins__church_id', onupdate="NO ACTION", ondelete="NO ACTION"),
        ForeignKeyConstraint(['user_id'], ['tb_users.id'], name='fk_church_admins__user_id', onupdate="NO ACTION", ondelete="NO ACTION"),
        Index('ix_church_admins__church_id', 'church_id'),
        Index('ix_church_admins__user_id', 'user_id'),
    )
