from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """기본 사용자 스키마"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str


class UserUpdate(UserBase):
    """사용자 수정 스키마"""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """데이터베이스 사용자 기본 스키마"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """일반 응답용 사용자 스키마"""
    pass


class UserInDB(UserInDBBase):
    """데이터베이스 전용 사용자 스키마"""
    hashed_password: str


class Token(BaseModel):
    """토큰 스키마"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenPayload(BaseModel):
    """토큰 페이로드 스키마"""
    sub: str  # 사용자 ID 또는 서비스 이름
    email: str  # 사용자 이메일
    name: Optional[str] = None  # 사용자 이름
    exp: int  # 만료 시간 (Unix timestamp)


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""
    email: EmailStr
    full_name: str


class PasswordReset(BaseModel):
    """비밀번호 재설정 스키마"""
    email: EmailStr
    full_name: str
    new_password: str
