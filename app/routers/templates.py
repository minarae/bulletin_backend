from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import schemas
from app.models import Church, ChurchAdmin, BulletinTemplate
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService
router = APIRouter()


@router.get("/{church_id}/", response_model=List[schemas.BulletinTemplate])
def read_templates(
    church_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 교회의 템플릿 목록을 반환합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted is False
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted is False
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 템플릿 목록 조회
    templates = db.query(BulletinTemplate).filter(
        BulletinTemplate.church_id == church_id,
        BulletinTemplate.is_deleted is False
    ).offset(skip).limit(limit).all()

    return templates


@router.post("/{church_id}/", response_model=schemas.BulletinTemplate)
def create_template(
    church_id: int,
    template: schemas.BulletinTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """새 템플릿을 생성합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted is False
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted is False
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 템플릿 생성
    new_template = BulletinTemplate(
        church_id=church_id,
        name=template.name,
        template_data=template.template_data
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


@router.get("/{church_id}/{template_id}", response_model=schemas.BulletinTemplate)
def read_template(
    church_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 템플릿 정보를 반환합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted is False
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted is False
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 템플릿 조회
    template = db.query(BulletinTemplate).filter(
        BulletinTemplate.id == template_id,
        BulletinTemplate.church_id == church_id,
        BulletinTemplate.is_deleted is False
    ).first()

    if template is None:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    return template


@router.put("/{church_id}/{template_id}", response_model=schemas.BulletinTemplate)
def update_template(
    church_id: int,
    template_id: int,
    template_update: schemas.BulletinTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """템플릿 정보를 수정합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted is False
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted is False
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 템플릿 조회
    template = db.query(BulletinTemplate).filter(
        BulletinTemplate.id == template_id,
        BulletinTemplate.church_id == church_id,
        BulletinTemplate.is_deleted is False
    ).first()

    if template is None:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 템플릿 정보 업데이트
    update_data = template_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/{church_id}/{template_id}")
def delete_template(
    church_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """템플릿을 삭제합니다."""
    # 교회 조회
    db_church = db.query(Church).filter(
        Church.id == church_id,
        Church.is_deleted is False
    ).first()

    if db_church is None:
        raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

    # 권한 확인
    is_admin = db.query(ChurchAdmin).filter(
        ChurchAdmin.church_id == church_id,
        ChurchAdmin.user_id == current_user.id,
        ChurchAdmin.is_deleted is False
    ).first()

    if not is_admin:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 템플릿 조회
    template = db.query(BulletinTemplate).filter(
        BulletinTemplate.id == template_id,
        BulletinTemplate.church_id == church_id,
        BulletinTemplate.is_deleted is False
    ).first()

    if template is None:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 템플릿 삭제 처리 (소프트 삭제)
    template.is_deleted = True
    template.deleted_at = datetime.now()
    db.commit()

    return {"detail": "템플릿이 삭제되었습니다"}