from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
import uuid
from datetime import datetime

from app.db.session import get_db
from app.services.auth import AuthService
from app.models.user import User
from app.models.church import Church

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
    responses={404: {"description": "Not found"}},
)

# 이미지 저장 경로 설정
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    church_id: Optional[int] = None,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """
    이미지 파일을 업로드합니다.
    """
    # 교회 ID가 제공된 경우 해당 교회에 대한 권한 확인
    if church_id:
        church = db.query(Church).filter(Church.id == church_id).first()
        if not church:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="교회를 찾을 수 없습니다."
            )

        # 교회 관리자 또는 슈퍼유저만 업로드 가능
        if church.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 교회에 대한 업로드 권한이 없습니다."
            )

    # 파일 확장자 확인
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원되지 않는 파일 형식입니다. JPG, PNG, GIF 파일만 업로드 가능합니다."
        )

    # 고유한 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = f"{timestamp}_{uuid.uuid4()}{file_ext}"

    # 교회별 디렉토리 생성
    church_dir = os.path.join(UPLOAD_DIR, f"church_{church_id}" if church_id else "general")
    os.makedirs(church_dir, exist_ok=True)

    # 파일 저장 경로
    file_path = os.path.join(church_dir, unique_filename)

    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 파일 URL 생성 (상대 경로)
    file_url = f"/static/{file_path}"

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"url": file_url, "filename": unique_filename}
    )
