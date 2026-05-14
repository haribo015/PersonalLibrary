from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    # Keep basic input limits in the schema so invalid payloads fail before persistence.
    email: EmailStr
    name: str = Field(min_length=2, max_length=128)
    password: str = Field(min_length=8, max_length=512)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Never expose hashed_password in read models.
    id: int
    email: EmailStr
    name: str
    is_active: bool
    reading_goal: int
