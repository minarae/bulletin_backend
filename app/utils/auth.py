from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.church import Church, ChurchAdmin


def check_church_admin_permission(
    db: Session,
    user: User,
    church_id: int
) -> bool:
    """
    사용자가 특정 교회의 관리자 권한이 있는지 확인합니다.
    슈퍼유저의 경우 모든 교회에 대한 권한을 가집니다.
    """
    if user.is_superuser:
        return True

    return db.query(ChurchAdmin).filter(
        ChurchAdmin.user_id == user.id,
        ChurchAdmin.church_id == church_id
    ).first() is not None


def get_user_churches(
    db: Session,
    user: User
) -> list[Church]:
    """
    사용자가 관리자 권한을 가진 교회 목록을 반환합니다.
    슈퍼유저의 경우 모든 교회 목록을 반환합니다.
    """
    if user.is_superuser:
        return db.query(Church).all()

    return db.query(Church).join(ChurchAdmin).filter(
        ChurchAdmin.user_id == user.id
    ).all()


def add_church_admin(
    db: Session,
    user_id: int,
    church_id: int
) -> Optional[ChurchAdmin]:
    """
    사용자에게 특정 교회의 관리자 권한을 부여합니다.
    이미 권한이 있는 경우 None을 반환합니다.
    """
    existing = db.query(ChurchAdmin).filter(
        ChurchAdmin.user_id == user_id,
        ChurchAdmin.church_id == church_id
    ).first()

    if existing:
        return None

    admin = ChurchAdmin(user_id=user_id, church_id=church_id)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def remove_church_admin(
    db: Session,
    user_id: int,
    church_id: int
) -> bool:
    """
    사용자의 특정 교회 관리자 권한을 제거합니다.
    제거된 경우 True를 반환합니다.
    """
    result = db.query(ChurchAdmin).filter(
        ChurchAdmin.user_id == user_id,
        ChurchAdmin.church_id == church_id
    ).delete()

    db.commit()
    return result > 0