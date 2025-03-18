from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    Date,
    CHAR,
    Sequence,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class BulletinTemplate(Base):
    __tablename__ = "tb_bulletin_templates"

    id = Column(Integer, Sequence("seq_bulletin_templates"), nullable=False, comment="주보 템플릿 ID")
    church_id = Column(Integer, nullable=False, comment="교회 ID")
    name = Column(String, nullable=False, comment="템플릿 이름")
    template_data = Column(JSON, nullable=False, comment="기본 템플릿 데이터")  # 기본 템플릿 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(1), nullable=False, default="F", comment="삭제 여부")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="삭제일시")

    # 각 교회 내에서 템플릿 이름은 고유해야 함 (복합 유니크 제약조건)
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_bulletin_templates"),
        ForeignKeyConstraint(['church_id'], ['tb_churches.id'], name='fk_bulletin_templates__church_id', onupdate="NO ACTION", ondelete="NO ACTION"),
        Index('ix_bulletin_templates__church_id', 'church_id'),
    )

    # Relationships
    church = relationship("Church", back_populates="templates")
    bulletins = relationship("Bulletin", back_populates="template")


class Bulletin(Base):
    __tablename__ = "tb_bulletins"

    id = Column(Integer, Sequence("seq_bulletins"), nullable=False, comment="주보 ID")
    church_id = Column(Integer, nullable=False, comment="교회 ID")
    template_id = Column(Integer, nullable=True, comment="템플릿 ID")
    year = Column(Integer, nullable=False, comment="주보 연도")
    month = Column(Integer, nullable=False, comment="주보 월")
    date = Column(Date, nullable=False, comment="주보 날짜")
    content = Column(JSON, nullable=False, comment="실제 주보 내용")  # 실제 주보 내용
    is_published = Column(CHAR(1), nullable=False, default="F", comment="게시 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(1), nullable=False, default="F", comment="삭제 여부")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="삭제일시")

    # 각 교회는 특정 날짜에 하나의 주보만 가질 수 있음 (복합 유니크 제약조건)
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_bulletins"),
        ForeignKeyConstraint(['church_id'], ['tb_churches.id'], name='fk_bulletins__church_id', onupdate="NO ACTION", ondelete="NO ACTION"),
        ForeignKeyConstraint(['template_id'], ['tb_bulletin_templates.id'], name='fk_bulletins__template_id', onupdate="NO ACTION", ondelete="NO ACTION"),
        Index('ix_bulletins__date', 'date'),
        Index('ix_bulletins__church_id', 'church_id'),
        Index('ix_bulletins__template_id', 'template_id'),
        Index('ix_bulletins__year', 'year'),
        Index('ix_bulletins__concatenated0', 'year', 'month'),
    )

    # Relationships
    church = relationship("Church", back_populates="bulletins")
    template = relationship("BulletinTemplate", back_populates="bulletins")
