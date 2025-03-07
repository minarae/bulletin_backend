from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Church(Base):
    __tablename__ = "tb_churches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String)
    contact_info = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    admins = relationship("ChurchAdmin", back_populates="church")
    bulletins = relationship("Bulletin", back_populates="church")
    templates = relationship("BulletinTemplate", back_populates="church")


class ChurchAdmin(Base):
    __tablename__ = "tb_church_admins"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("tb_churches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("tb_users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    church = relationship("Church", back_populates="admins")
    user = relationship("User", back_populates="church_admin_roles")
