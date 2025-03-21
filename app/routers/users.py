import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate
from app.services.auth import AuthService
from app.services.user import UserService

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def get_current_user(
    current_user: User = Depends(AuthService.get_current_user),
) -> User:
    """현재 로그인한 사용자 정보 조회"""
    logger.info(f"Getting current user info: {current_user.email}")
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
    user_in: UserUpdate,
) -> User:
    """현재 로그인한 사용자 정보 수정"""
    logger.info(f"Updating user info for: {current_user.email}")
    return UserService.update(db=db, db_user=current_user, user_in=user_in)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
) -> None:
    """현재 로그인한 사용자 삭제"""
    logger.info(f"Deleting user: {current_user.email}")
    UserService.delete(db=db, user_id=current_user.id)
