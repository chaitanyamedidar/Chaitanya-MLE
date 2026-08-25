from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.services import auth as auth_svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if auth_svc.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = auth_svc.create_user(db, payload.email, payload.password)
    return TokenResponse(access_token=auth_svc.create_token(user.id), email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_svc.get_user_by_email(db, payload.email)
    if user is None or not auth_svc.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=auth_svc.create_token(user.id), email=user.email)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=user.id,
        email=user.email,
        gemini_enabled=bool(settings.gemini_api_key),
    )
