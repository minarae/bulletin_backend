from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService
from app.services.church import ChurchService

router = APIRouter()


@router.get("/", response_model=List[schemas.Church])
def read_churches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """현재 로그인한 사용자가 관리하는 교회 목록을 반환합니다."""
    return ChurchService.get_churches_by_user(db, current_user.id, skip, limit)


@router.post("/", response_model=schemas.Church)
def create_church(
    church: schemas.ChurchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """새 교회를 생성합니다."""
    return ChurchService.create_church(db, church, current_user.id)


@router.get("/check-code/{church_code}", response_model=schemas.ChurchCheck)
def check_church_code(church_code: str, db: Session = Depends(get_db)):
    """교회 구분값 중복 확인"""
    return ChurchService.check_church_code(db, church_code)


@router.get("/{church_id}", response_model=schemas.Church)
def read_church(
    church_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 교회 정보를 반환합니다."""
    return ChurchService.get_church_with_permission_check(db, church_id, current_user.id)


@router.put("/{church_id}", response_model=schemas.Church)
def update_church(
    church_id: int,
    church: schemas.ChurchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """교회 정보를 수정합니다."""
    return ChurchService.update_church(db, church_id, church, current_user.id)


@router.delete("/{church_id}")
def delete_church(
    church_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """교회를 삭제합니다."""
    return ChurchService.delete_church(db, church_id, current_user.id)
