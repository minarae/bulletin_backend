from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService
from app.services.template import TemplateService

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
    return TemplateService.get_templates_by_church(db, church_id, current_user.id, skip, limit)


@router.post("/{church_id}/", response_model=schemas.BulletinTemplate)
def create_template(
    church_id: int,
    template: schemas.BulletinTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """새 템플릿을 생성합니다."""
    return TemplateService.create_template(db, church_id, current_user.id, template)


@router.get("/{church_id}/{template_id}", response_model=schemas.BulletinTemplate)
def read_template(
    church_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 템플릿 정보를 반환합니다."""
    return TemplateService.get_template(db, church_id, template_id, current_user.id)


@router.put("/{church_id}/{template_id}", response_model=schemas.BulletinTemplate)
def update_template(
    church_id: int,
    template_id: int,
    template_update: schemas.BulletinTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """템플릿 정보를 수정합니다."""
    update_data = template_update.dict(exclude_unset=True)
    return TemplateService.update_template(db, church_id, template_id, current_user.id, update_data)


@router.delete("/{church_id}/{template_id}")
def delete_template(
    church_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """템플릿을 삭제합니다."""
    return TemplateService.delete_template(db, church_id, template_id, current_user.id)


@router.post("/{church_id}/{template_id}/copy", response_model=schemas.BulletinTemplate)
def copy_template(
    church_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """기존 템플릿을 복사하여 새 템플릿을 생성합니다."""
    return TemplateService.copy_template(db, church_id, template_id, current_user.id)
