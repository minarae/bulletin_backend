from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService
from app.services.bulletin import BulletinService

router = APIRouter()


@router.get("/{church_id}/", response_model=List[schemas.Bulletin])
def read_bulletins(
    church_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 교회의 주보 목록을 반환합니다."""
    return BulletinService.get_bulletins_by_church(db, church_id, current_user.id, skip, limit)


@router.post("/{church_id}/", response_model=schemas.Bulletin)
def create_bulletin(
    church_id: int,
    bulletin: schemas.BulletinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """새 주보를 생성합니다."""
    return BulletinService.create(db, church_id, current_user, bulletin)


@router.get("/{church_id}/{bulletin_id}", response_model=schemas.Bulletin)
def read_bulletin(
    church_id: int,
    bulletin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 주보 정보를 반환합니다."""
    return BulletinService.get_bulletin(db, church_id, bulletin_id, current_user.id)


@router.put("/{church_id}/{bulletin_id}", response_model=schemas.Bulletin)
def update_bulletin(
    church_id: int,
    bulletin_id: int,
    bulletin_update: schemas.BulletinUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """주보 정보를 수정합니다."""
    update_data = bulletin_update.dict(exclude_unset=True)
    return BulletinService.update_bulletin(db, church_id, bulletin_id, current_user.id, update_data)


@router.delete("/{church_id}/{bulletin_id}")
def delete_bulletin(
    church_id: int,
    bulletin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """주보를 삭제합니다."""
    return BulletinService.delete_bulletin(db, church_id, bulletin_id, current_user.id)


@router.patch("/{church_id}/{bulletin_id}/publish", response_model=schemas.Bulletin)
def update_bulletin_publish_status(
    church_id: int,
    bulletin_id: int,
    publish_data: schemas.BulletinPublish,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """주보의 게시 상태를 변경합니다."""
    return BulletinService.update_publish_status(
        db, church_id, bulletin_id, current_user.id, publish_data
    )
