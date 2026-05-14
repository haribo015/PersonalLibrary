from typing import Annotated

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import get_db
from app.repositories.auth.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserRead
from app.services.auth.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    service = AuthService(UserRepository(db))
    user = await service.register_user(user_in)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email deja utilise")
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # OAuth2PasswordRequestForm is kept for tool compatibility with FastAPI docs
    # and standard API clients, even though the frontend submits a simple login form.
    service = AuthService(UserRepository(db))
    user = await service.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les informations d'identification",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}
