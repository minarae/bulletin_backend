from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Bulletin, BulletinTemplate
from app.schemas import BulletinCreate, BulletinPublish
from app.models.user import User
from fastapi import HTTPException
from app.services.church import ChurchService


class BulletinService:

    @staticmethod
    def create(
        db: Session,
        church_id: int,
        current_user: User,
        bulletin: BulletinCreate
    ) -> Bulletin:
        """주보 생성"""
        # 교회 접근 권한 확인
        ChurchService.check_church_access(db, church_id, current_user.id)

        # 템플릿 확인
        template = db.query(BulletinTemplate).filter(
            BulletinTemplate.id == bulletin.template_id,
            BulletinTemplate.church_id == church_id,
            BulletinTemplate.is_deleted == 'F'
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

    @staticmethod
    def get_bulletins_by_church(
        db: Session,
        church_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Bulletin]:
        """교회별 주보 목록 조회"""
        # 교회 접근 권한 확인
        ChurchService.check_church_access(db, church_id, user_id)

        # 주보 목록 조회
        bulletins = db.query(Bulletin).filter(
            Bulletin.church_id == church_id,
            Bulletin.is_deleted == 'F'
        ).order_by(Bulletin.date.desc()).offset(skip).limit(limit).all()

        return bulletins

    @staticmethod
    def check_bulletin_access(
        db: Session,
        church_id: int,
        bulletin_id: int,
        user_id: int
    ) -> Bulletin:
        """주보 접근 권한 확인 및 주보 조회"""
        # 교회 접근 권한 확인
        ChurchService.check_church_access(db, church_id, user_id)

        # 주보 조회
        bulletin = db.query(Bulletin).filter(
            Bulletin.id == bulletin_id,
            Bulletin.church_id == church_id,
            Bulletin.is_deleted == 'F'
        ).first()

        if bulletin is None:
            raise HTTPException(status_code=404, detail="주보를 찾을 수 없습니다")

        return bulletin

    @staticmethod
    def get_bulletin(
        db: Session,
        church_id: int,
        bulletin_id: int,
        user_id: int
    ) -> Bulletin:
        """특정 주보 정보 조회"""
        return BulletinService.check_bulletin_access(db, church_id, bulletin_id, user_id)

    @staticmethod
    def update_bulletin(
        db: Session,
        church_id: int,
        bulletin_id: int,
        user_id: int,
        bulletin_update_data: dict
    ) -> Bulletin:
        """주보 정보 수정"""
        # 주보 접근 권한 확인 및 주보 조회
        bulletin = BulletinService.check_bulletin_access(db, church_id, bulletin_id, user_id)

        # 템플릿 변경 시 확인
        if bulletin_update_data.get('template_id') is not None:
            template = db.query(BulletinTemplate).filter(
                BulletinTemplate.id == bulletin_update_data['template_id'],
                BulletinTemplate.church_id == church_id,
                BulletinTemplate.is_deleted == 'F'
            ).first()

            if template is None:
                raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

        # 주보 정보 업데이트
        for key, value in bulletin_update_data.items():
            setattr(bulletin, key, value)

        db.commit()
        db.refresh(bulletin)
        return bulletin

    @staticmethod
    def delete_bulletin(
        db: Session,
        church_id: int,
        bulletin_id: int,
        user_id: int
    ) -> dict:
        """주보 삭제"""
        # 주보 접근 권한 확인 및 주보 조회
        bulletin = BulletinService.check_bulletin_access(db, church_id, bulletin_id, user_id)

        # 주보 삭제 처리 (소프트 삭제)
        bulletin.is_deleted = 'T'
        bulletin.deleted_at = datetime.now()
        db.commit()

        return {"detail": "주보가 삭제되었습니다"}

    @staticmethod
    def update_publish_status(
        db: Session,
        church_id: int,
        bulletin_id: int,
        user_id: int,
        publish_data: BulletinPublish
    ) -> Bulletin:
        """주보 게시 상태 변경"""
        # 주보 접근 권한 확인 및 주보 조회
        bulletin = BulletinService.check_bulletin_access(db, church_id, bulletin_id, user_id)

        # 게시 상태 업데이트
        bulletin.is_published = 'T' if publish_data.is_published else 'F'
        db.commit()
        db.refresh(bulletin)

        return bulletin
