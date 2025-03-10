from datetime import datetime
import logging
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.deps import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

# 로깅 설정
logger = logging.getLogger(__name__)

# 비밀번호 해시화 설정 - SHA-256 사용
pwd_context = CryptContext(
    schemes=["sha256_crypt"],
    deprecated="auto",
)
# 토큰 URL을 auth/login으로 설정 (API 경로에 맞게)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
    def create_access_token(user: User) -> str:
        """액세스 토큰 생성"""
        # 현재 시간을 Unix timestamp로 가져옴
        now = int(time.time())
        # 만료 시간 계산 (초 단위)
        expires = now + settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600

        # JWT 표준에 맞게 exp는 초 단위 타임스탬프로 설정
        to_encode = {
            "iat": now,  # 발급 시간
            "exp": expires,  # 만료 시간
            "sub": str(user.id),
            "email": user.email,
            "name": user.full_name
        }
        logger.info(f"Creating access token for user {user.id} with iat: {now}, exp: {expires}")
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user: User) -> str:
        """리프레시 토큰 생성"""
        # 현재 시간을 Unix timestamp로 가져옴
        now = int(time.time())
        # 만료 시간 계산 (초 단위)
        expires = now + settings.REFRESH_TOKEN_EXPIRE_HOURS * 3600

        # JWT 표준에 맞게 exp는 초 단위 타임스탬프로 설정
        to_encode = {
            "iat": now,  # 발급 시간
            "exp": expires,  # 만료 시간
            "sub": str(user.id),
            "email": user.email,
            "name": user.full_name
        }
        logger.info(f"Creating refresh token for user {user.id} with iat: {now}, exp: {expires}")
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
            logger.info(f"Decoding token: {token[:10]}...")
            secret_key = settings.REFRESH_SECRET_KEY if refresh else settings.SECRET_KEY

            # 현재 시간 로깅
            now = int(time.time())
            logger.info(f"Current time (Unix timestamp): {now}")

            # 토큰 검증 시 만료 시간 검증을 jose 라이브러리에 위임
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # 만료 시간 검증을 비활성화하고 수동으로 검증
            )
            logger.info(f"Token payload: {payload}")

            # TokenPayload 모델로 변환
            token_data = TokenPayload(**payload)

            # 현재 시간과 만료 시간 로깅
            exp_time = datetime.fromtimestamp(token_data.exp)
            logger.info(f"Current time: {datetime.utcnow()}, Token expiry: {exp_time}")

            # 수동으로 만료 시간 검증 (10초의 여유 시간 허용)
            if token_data.exp < now - 10:
                logger.warning(f"Token expired: exp={token_data.exp}, now={now}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return token_data
        except JWTError as e:
            logger.error(f"JWT Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> User:
        """현재 인증된 사용자 조회"""
        try:
            logger.info(f"Getting current user with token: {token[:10]}...")
            token_data = AuthService.decode_token(token)
            logger.info(f"Token data: {token_data}")
            user = db.query(User).filter(User.id == int(token_data.sub)).first()
            if not user:
                logger.warning(f"User with ID {token_data.sub} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user
        except ValueError as e:
            logger.error(f"Value Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
