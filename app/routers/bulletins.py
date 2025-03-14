from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import schemas
from app.models import Church, ChurchAdmin, Bulletin, BulletinTemplate
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService
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
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted == False  # noqa: E712
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted == False  # noqa: E712
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 주보 목록 조회
    bulletins = db.query(Bulletin).filter(
        Bulletin.church_id == church_id,
        Bulletin.is_deleted is False
    ).order_by(Bulletin.date.desc()).offset(skip).limit(limit).all()

    return bulletins


@router.post("/{church_id}/", response_model=schemas.Bulletin)
def create_bulletin(
    church_id: int,
    bulletin: schemas.BulletinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """새 주보를 생성합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted == False  # noqa: E712
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted == False  # noqa: E712
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 템플릿 확인
    template = db.query(BulletinTemplate).filter(
        BulletinTemplate.id == bulletin.template_id,
        BulletinTemplate.church_id == church_id,
        BulletinTemplate.is_deleted is False
    ).first()

    if template is None:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 주보 생성
    new_bulletin = Bulletin(
        church_id=church_id,
        template_id=bulletin.template_id,
        date=bulletin.date,
        content=bulletin.content
    )
    db.add(new_bulletin)
    db.commit()
    db.refresh(new_bulletin)

    return new_bulletin


@router.get("/{church_id}/{bulletin_id}", response_model=schemas.Bulletin)
def read_bulletin(
    church_id: int,
    bulletin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 주보 정보를 반환합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted == False  # noqa: E712
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted == False  # noqa: E712
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 주보 조회
    bulletin = db.query(Bulletin).filter(
        Bulletin.id == bulletin_id,
        Bulletin.church_id == church_id,
        Bulletin.is_deleted is False
    ).first()

    if bulletin is None:
        raise HTTPException(status_code=404, detail="주보를 찾을 수 없습니다")

    return bulletin


@router.put("/{church_id}/{bulletin_id}", response_model=schemas.Bulletin)
def update_bulletin(
    church_id: int,
    bulletin_id: int,
    bulletin_update: schemas.BulletinUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """주보 정보를 수정합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted == False  # noqa: E712
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted == False  # noqa: E712
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 주보 조회
    bulletin = db.query(Bulletin).filter(
        Bulletin.id == bulletin_id,
        Bulletin.church_id == church_id,
        Bulletin.is_deleted is False
    ).first()

    if bulletin is None:
        raise HTTPException(status_code=404, detail="주보를 찾을 수 없습니다")

    # 템플릿 변경 시 확인
    if bulletin_update.template_id is not None:
        template = db.query(BulletinTemplate).filter(
            BulletinTemplate.id == bulletin_update.template_id,
            BulletinTemplate.church_id == church_id,
            BulletinTemplate.is_deleted is False
        ).first()

        if template is None:
            raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 주보 정보 업데이트
    update_data = bulletin_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bulletin, key, value)

    db.commit()
    db.refresh(bulletin)
    return bulletin


@router.delete("/{church_id}/{bulletin_id}")
def delete_bulletin(
    church_id: int,
    bulletin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """주보를 삭제합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted == False  # noqa: E712
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted == False  # noqa: E712
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 주보 조회
    bulletin = db.query(Bulletin).filter(
        Bulletin.id == bulletin_id,
        Bulletin.church_id == church_id,
        Bulletin.is_deleted is False
    ).first()

    if bulletin is None:
        raise HTTPException(status_code=404, detail="주보를 찾을 수 없습니다")

    # 주보 삭제 처리 (소프트 삭제)
    bulletin.is_deleted = True
    bulletin.deleted_at = datetime.now()
    db.commit()

    return {"detail": "주보가 삭제되었습니다"}
