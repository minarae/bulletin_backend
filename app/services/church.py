from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models import Church, ChurchAdmin
from app.schemas import ChurchCreate, ChurchUpdate, ChurchCheck


class ChurchService:
    """교회 관련 서비스 클래스"""

    @staticmethod
    def get_churches_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Church]:
        """사용자가 관리하는 교회 목록을 반환합니다."""
        churches = db.query(Church) \
            .join(ChurchAdmin, Church.id == ChurchAdmin.church_id) \
            .filter(and_(
                Church.is_deleted == 'F',
                ChurchAdmin.is_deleted == 'F',
                ChurchAdmin.user_id == user_id
            )).offset(skip).limit(limit).all()

        return churches

    @staticmethod
    def create_church(
        db: Session,
        church_data: ChurchCreate,
        user_id: int
    ) -> Church:
        """새 교회를 생성합니다."""
        # 교회 코드 중복 확인
        db_church = db.query(Church).filter(
            Church.church_code == church_data.church_code,
            Church.is_deleted == 'F'
        ).first()

        if db_church:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 교회 구분값입니다"
            )

        # 교회 생성
        new_church = Church(
            church_code=church_data.church_code,
            name=church_data.name,
            address=church_data.address,
            contact_info=church_data.contact_info
        )
        db.add(new_church)
        db.flush()

        # 교회 관리자 등록
        church_admin = ChurchAdmin(
            church_id=new_church.id,
            user_id=user_id
        )
        db.add(church_admin)
        db.commit()
        db.refresh(new_church)

        return new_church

    @staticmethod
    def check_church_code(db: Session, church_code: str) -> ChurchCheck:
        """교회 구분값 중복 확인"""
        db_church = db.query(Church).filter(
            Church.church_code == church_code,
            Church.is_deleted == 'F'
        ).first()

        if db_church:
            return {"available": False, "message": "이미 사용 중인 교회 구분값입니다"}
        return {"available": True, "message": "사용 가능한 교회 구분값입니다"}

    @staticmethod
    def get_church_by_id(db: Session, church_id: int) -> Optional[Church]:
        """ID로 교회를 조회합니다."""
        return db.query(Church).filter(
            Church.id == church_id,
            Church.is_deleted == 'F'
        ).first()

    @staticmethod
    def check_church_admin(db: Session, church_id: int, user_id: int) -> bool:
        """사용자가 해당 교회의 관리자인지 확인합니다."""
        is_admin = db.query(ChurchAdmin).filter(
            ChurchAdmin.church_id == church_id,
            ChurchAdmin.user_id == user_id,
            ChurchAdmin.is_deleted == 'F'
        ).first()
        return is_admin is not None

    @staticmethod
    def get_church_with_permission_check(
        db: Session,
        church_id: int,
        user_id: int
    ) -> Church:
        """교회를 조회하고 권한을 확인합니다."""
        # 교회 조회
        db_church = ChurchService.get_church_by_id(db, church_id)
        if db_church is None:
            raise HTTPException(status_code=404, detail="교회를 찾을 수 없습니다")

        # 권한 확인
        if not ChurchService.check_church_admin(db, church_id, user_id):
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

        return db_church

    @staticmethod
    def update_church(
        db: Session,
        church_id: int,
        church_data: ChurchUpdate,
        user_id: int
    ) -> Church:
        """교회 정보를 수정합니다."""
        # 교회 조회 및 권한 확인
        db_church = ChurchService.get_church_with_permission_check(db, church_id, user_id)

        # 교회 정보 업데이트
        update_data = church_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_church, key, value)

        db.commit()
        db.refresh(db_church)
        return db_church

    @staticmethod
    def delete_church(db: Session, church_id: int, user_id: int) -> dict:
        """교회를 삭제합니다."""
        # 교회 조회 및 권한 확인
        db_church = ChurchService.get_church_with_permission_check(db, church_id, user_id)

        # 교회 삭제 처리 (소프트 삭제)
        db_church.is_deleted = 'T'
        db_church.deleted_at = datetime.now()
        db.commit()

        return {"detail": "교회가 삭제되었습니다"}