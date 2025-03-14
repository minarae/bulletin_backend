from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class BulletinTemplateBase(BaseModel):
    """주보 템플릿 기본 스키마"""
    name: str
    template_data: Dict[str, Any]


class BulletinTemplateCreate(BulletinTemplateBase):
    """주보 템플릿 생성 스키마"""
    pass


class BulletinTemplateUpdate(BaseModel):
    """주보 템플릿 업데이트 스키마"""
    name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None


class BulletinTemplate(BulletinTemplateBase):
    """주보 템플릿 응답 스키마"""
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class BulletinBase(BaseModel):
    """주보 기본 스키마"""
    date: date
    content: Dict[str, Any]
    template_id: int


class BulletinCreate(BulletinBase):
    """주보 생성 스키마"""
    pass


class BulletinUpdate(BaseModel):
    """주보 업데이트 스키마"""
    date: Optional[date] = None
    content: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None


class Bulletin(BulletinBase):
    """주보 응답 스키마"""
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
