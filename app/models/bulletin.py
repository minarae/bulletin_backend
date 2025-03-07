from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class BulletinTemplate(Base):
    __tablename__ = "tb_bulletin_templates"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("tb_churches.id"), nullable=False)
    name = Column(String, nullable=False)
    template_data = Column(JSON, nullable=False)  # 기본 템플릿 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="templates")
    bulletins = relationship("Bulletin", back_populates="template")


class Bulletin(Base):
    __tablename__ = "tb_bulletins"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("tb_churches.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("tb_bulletin_templates.id"), nullable=False)
    date = Column(Date, nullable=False)
    content = Column(JSON, nullable=False)  # 실제 주보 내용
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="bulletins")
    template = relationship("BulletinTemplate", back_populates="bulletins")
