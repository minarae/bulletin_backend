from sqlalchemy.orm import Session

from app.models import Bulletin, Church, ChurchAdmin, BulletinTemplate
from app.schemas import BulletinCreate
from app.models.user import User
from fastapi import HTTPException


class BulletinService:

    @staticmethod
    def create(
        db: Session,
        church_id: int,
        current_user: User,
        bulletin: BulletinCreate
    ) -> Bulletin:
        """주보 생성"""
        db_church = db.query(Church).filter(
            Church.id == church_id,
            Church.is_deleted == 'F'
        ).first()

        if db_church is None:
            raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

        # 권한 확인
        is_admin = db.query(ChurchAdmin).filter(
            ChurchAdmin.church_id == church_id,
            ChurchAdmin.user_id == current_user.id,
            ChurchAdmin.is_deleted == 'F'
        ).first()

        if not is_admin:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

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
