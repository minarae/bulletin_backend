from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.deps import get_db
from app.schemas.user import Token, User, UserCreate
from app.services.auth import AuthService, oauth2_scheme
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
        "access_token": AuthService.create_access_token(user.id),
        "refresh_token": AuthService.create_refresh_token(user.id),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db),
    refresh_token: str = Depends(oauth2_scheme),
) -> Token:
    """리프레시 토큰을 사용하여 새로운 액세스 토큰 발급"""
    try:
        token_data = AuthService.decode_token(refresh_token, refresh=True)
        user = UserService.get_by_id(db=db, user_id=token_data.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return {
            "access_token": AuthService.create_access_token(user.id),
            "refresh_token": AuthService.create_refresh_token(user.id),
            "token_type": "bearer",
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
