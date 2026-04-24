from app.core.security import get_password_hash, verify_password
from app.repositories.auth.user_repository import UserRepository
from app.schemas.users import UserCreate


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register_user(self, user_in: UserCreate):
        existing = await self.user_repository.get_by_email(user_in.email)
        if existing is not None:
            return None
        return await self.user_repository.create(
            email=user_in.email,
            name=user_in.name,
            hashed_password=get_password_hash(user_in.password),
        )

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user
