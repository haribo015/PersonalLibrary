from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    # OAuth2-compatible response shape consumed by Angular and FastAPI docs.
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    # Decoded claims are optional because invalid/expired tokens are handled by dependencies.
    sub: Optional[str] = None
    exp: Optional[int] = None
