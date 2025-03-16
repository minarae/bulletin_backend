from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime

from app import schemas
from app.models import Church, ChurchAdmin
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService

router = APIRouter()


@router.get("/", response_model=List[schemas.Church])
def read_churches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """현재 로그인한 사용자가 관리하는 교회 목록을 반환합니다."""
    # 사용자가 관리하는 교회 ID 목록 조회
    print(f"current_user: {current_user}")

    churches = db.query(Church) \
        .join(ChurchAdmin, Church.id == ChurchAdmin.church_id) \
        .filter(and_(
            Church.is_deleted == 'F',
            ChurchAdmin.is_deleted == 'F',
            ChurchAdmin.user_id == current_user.id
        )).offset(skip).limit(limit).all()

    return churches

    return churches


@router.post("/", response_model=schemas.Church)
def create_church(
    church: schemas.ChurchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """새 교회를 생성합니다."""
    # 교회 코드 중복 확인
    db_church = db.query(Church).filter(
        Church.church_code == church.church_code,
        Church.is_deleted == 'F'
    ).first()

    if db_church:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 교회 구분값입니다"
        )

    # 교회 생성
    new_church = Church(
        church_code=church.church_code,
        name=church.name,
        address=church.address,
        contact_info=church.contact_info
    )
    db.add(new_church)
    db.flush()

    # 교회 관리자 등록
    church_admin = ChurchAdmin(
        church_id=new_church.id,
        user_id=current_user.id
    )
    db.add(church_admin)
    db.commit()
    db.refresh(new_church)

    return new_church


@router.get("/check-code/{church_code}", response_model=schemas.ChurchCheck)
def check_church_code(church_code: str, db: Session = Depends(get_db)):
    """교회 구분값 중복 확인"""
    db_church = db.query(Church).filter(
        Church.church_code == church_code,
        Church.is_deleted == 'F'
    ).first()

    if db_church:
        return {"available": False, "message": "이미 사용 중인 교회 구분값입니다"}
    return {"available": True, "message": "사용 가능한 교회 구분값입니다"}


@router.get("/{church_id}", response_model=schemas.Church)
def read_church(
    church_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """특정 교회 정보를 반환합니다."""
    # 교회 조회
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

    return db_church


@router.put("/{church_id}", response_model=schemas.Church)
def update_church(
    church_id: int,
    church: schemas.ChurchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """교회 정보를 수정합니다."""
    # 교회 조회
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

    # 교회 정보 업데이트
    update_data = church.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_church, key, value)

    db.commit()
    db.refresh(db_church)
    return db_church


@router.delete("/{church_id}")
def delete_church(
    church_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """교회를 삭제합니다."""
    # 교회 조회
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

    # 교회 삭제 처리 (소프트 삭제)
    db_church.is_deleted = True
    db_church.deleted_at = datetime.now()
    db.commit()

    return {"detail": "교회가 삭제되었습니다"}
