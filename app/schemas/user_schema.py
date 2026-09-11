from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


UserRole = Literal["admin", "support", "user"]


class UserCreate(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    role: UserRole
    is_active: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
