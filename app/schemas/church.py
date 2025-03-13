from typing import Optional
from pydantic import BaseModel, validator
import re
from datetime import datetime


class ChurchBase(BaseModel):
    """교회 기본 스키마"""
    name: str
    address: Optional[str] = None
    contact_info: Optional[str] = None


class ChurchCreate(ChurchBase):
    """교회 생성 스키마"""
    church_code: str

    @validator('church_code')
    def church_code_must_be_english(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('교회 구분값은 영문, 숫자, 하이픈, 언더스코어만 사용 가능합니다')
        return v


class ChurchUpdate(BaseModel):
    """교회 업데이트 스키마"""
    name: Optional[str] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None


class ChurchCheck(BaseModel):
    """교회 코드 중복 확인 응답 스키마"""
    available: bool
    message: Optional[str] = None


class Church(ChurchBase):
    """교회 응답 스키마"""
    id: int
    church_code: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

    class Config:
        orm_mode = True