from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.deps import get_db
from app.schemas.user import Token, User, UserCreate, PasswordResetRequest, PasswordReset
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()


@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> User:
    """새로운 사용자 등록"""
    return UserService.create(db=db, user_in=user_in)


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """사용자 로그인 및 토큰 발급"""
    user = UserService.authenticate(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return {
        "access_token": AuthService.create_access_token(user),
        "refresh_token": AuthService.create_refresh_token(user),
        "token_type": "Bearer",
    }


class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 요청 스키마"""
    refresh_token: str


@router.post("/refresh", response_model=Token)
def refresh_token(
    *,
    db: Session = Depends(get_db),
    token_data: RefreshTokenRequest,
) -> Token:
    """리프레시 토큰을 사용하여 새로운 액세스 토큰 발급"""
    try:
        token_payload = AuthService.decode_token(token_data.refresh_token, refresh=True)
        user = UserService.get_by_id(db=db, user_id=token_payload.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return {
            "access_token": AuthService.create_access_token(user),
            "refresh_token": AuthService.create_refresh_token(user),
            "token_type": "Bearer",
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/check-reset-eligibility", response_model=dict)
def check_reset_eligibility(
    *,
    db: Session = Depends(get_db),
    reset_request: PasswordResetRequest,
) -> dict:
    """비밀번호 재설정 자격 확인"""
    user = UserService.get_by_email(db=db, email=reset_request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.full_name != reset_request.full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name does not match",
        )

    return {"eligible": True, "message": "User is eligible for password reset"}


@router.post("/reset-password", response_model=dict)
def reset_password(
    *,
    db: Session = Depends(get_db),
    reset_data: PasswordReset,
) -> dict:
    """비밀번호 재설정"""
    user = UserService.get_by_email(db=db, email=reset_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.full_name != reset_data.full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name does not match",
        )

    # 비밀번호 업데이트
    user.hashed_password = AuthService.get_password_hash(reset_data.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "Password has been reset successfully"}
