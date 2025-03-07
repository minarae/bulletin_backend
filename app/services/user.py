from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import AuthService


class UserService:
    """사용자 관련 서비스 클래스"""

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """사용자 생성"""
        # 이메일 중복 확인
        if UserService.get_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # 사용자 생성
        db_user = User(
            email=user_in.email,
            hashed_password=AuthService.get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(
        db: Session,
        db_user: User,
        user_in: UserUpdate,
    ) -> User:
        """사용자 정보 수정"""
        # 수정할 데이터 준비
        update_data = user_in.model_dump(exclude_unset=True)

        # 비밀번호가 있는 경우 해시화
        if "password" in update_data:
            update_data["hashed_password"] = AuthService.get_password_hash(
                update_data.pop("password")
            )

        # 데이터 수정
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """사용자 삭제"""
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """사용자 인증"""
        user = UserService.get_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user