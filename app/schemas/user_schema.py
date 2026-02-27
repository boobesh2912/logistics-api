# app/schemas/user_schema.py
from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    role: str