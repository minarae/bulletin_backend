from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.deps import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthService:
    """인증 관련 서비스 클래스"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해시화"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(subject: int) -> str:
        """액세스 토큰 생성"""
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        expire = datetime.utcnow() + expires_delta

        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(subject: int) -> str:
        """리프레시 토큰 생성"""
        expires_delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
        expire = datetime.utcnow() + expires_delta

        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode,
            settings.REFRESH_SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str, refresh: bool = False) -> TokenPayload:
        """토큰 디코딩"""
        try:
            secret_key = settings.REFRESH_SECRET_KEY if refresh else settings.SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
            token_data = TokenPayload(**payload)

            if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                )
            return token_data
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    @staticmethod
    async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> User:
        """현재 인증된 사용자 조회"""
        try:
            token_data = AuthService.decode_token(token)
            user = db.query(User).filter(User.id == int(token_data.sub)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
            )
