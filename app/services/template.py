from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from app.models import BulletinTemplate
from app.schemas import BulletinTemplateCreate
from fastapi import HTTPException
from app.services.church import ChurchService


class TemplateService:
    """템플릿 관련 서비스 클래스"""

    @staticmethod
    def get_templates_by_church(
        db: Session,
        church_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[BulletinTemplate]:
        """교회별 템플릿 목록 조회"""
        # 교회 접근 권한 확인
        ChurchService.check_church_access(db, church_id, user_id)

        # 템플릿 목록 조회
        templates = db.query(BulletinTemplate).filter(
            BulletinTemplate.church_id == church_id,
            BulletinTemplate.is_deleted == 'F'
        ).offset(skip).limit(limit).all()

        return templates

    @staticmethod
    def create_template(
        db: Session,
        church_id: int,
        user_id: int,
        template_data: BulletinTemplateCreate
    ) -> BulletinTemplate:
        """새로운 템플릿 생성"""
        # 교회 접근 권한 확인
        ChurchService.check_church_access(db, church_id, user_id)

        # 템플릿 생성
        new_template = BulletinTemplate(
            church_id=church_id,
            name=template_data.name,
            template_data=template_data.template_data
        )
        db.add(new_template)
        db.commit()
        db.refresh(new_template)

        return new_template

    @staticmethod
    def check_template_access(
        db: Session,
        church_id: int,
        template_id: int,
        user_id: int
    ) -> BulletinTemplate:
        """템플릿 접근 권한 확인 및 템플릿 조회"""
        # 교회 접근 권한 확인
        ChurchService.check_church_access(db, church_id, user_id)

        # 템플릿 조회
        template = db.query(BulletinTemplate).filter(
            BulletinTemplate.id == template_id,
            BulletinTemplate.church_id == church_id,
            BulletinTemplate.is_deleted == 'F'
        ).first()

        if template is None:
            raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

        return template

    @staticmethod
    def get_template(
        db: Session,
        church_id: int,
        template_id: int,
        user_id: int
    ) -> BulletinTemplate:
        """특정 템플릿 정보 조회"""
        return TemplateService.check_template_access(db, church_id, template_id, user_id)

    @staticmethod
    def update_template(
        db: Session,
        church_id: int,
        template_id: int,
        user_id: int,
        template_update_data: Dict[str, Any]
    ) -> BulletinTemplate:
        """템플릿 정보 수정"""
        # 템플릿 접근 권한 확인 및 템플릿 조회
        template = TemplateService.check_template_access(db, church_id, template_id, user_id)

        # 템플릿 정보 업데이트
        for key, value in template_update_data.items():
            setattr(template, key, value)

        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def delete_template(
        db: Session,
        church_id: int,
        template_id: int,
        user_id: int
    ) -> Dict[str, str]:
        """템플릿 삭제"""
        # 템플릿 접근 권한 확인 및 템플릿 조회
        template = TemplateService.check_template_access(db, church_id, template_id, user_id)

        # 템플릿 삭제 처리 (소프트 삭제)
        template.is_deleted = 'T'
        template.deleted_at = datetime.now()
        db.commit()

        return {"detail": "템플릿이 삭제되었습니다"}

    @staticmethod
    def copy_template(
        db: Session,
        church_id: int,
        template_id: int,
        user_id: int
    ) -> BulletinTemplate:
        """템플릿 복사"""
        # 원본 템플릿 접근 권한 확인 및 조회
        original_template = TemplateService.check_template_access(db, church_id, template_id, user_id)

        # 복사된 템플릿 생성
        new_template = BulletinTemplate(
            church_id=church_id,
            name=f"{original_template.name} (복사본)",
            template_data=original_template.template_data
        )
        db.add(new_template)
        db.commit()
        db.refresh(new_template)

        return new_template