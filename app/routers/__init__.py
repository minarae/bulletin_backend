from fastapi import APIRouter
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.churches import router as churches_router
from app.routers.bulletins import router as bulletins_router
from app.routers.templates import router as templates_router
from app.routers.uploads import router as uploads_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(churches_router, prefix="/churches", tags=["churches"])
router.include_router(bulletins_router, prefix="/bulletins", tags=["bulletins"])
router.include_router(templates_router, prefix="/templates", tags=["templates"])
router.include_router(uploads_router, prefix="/uploads", tags=["uploads"])
