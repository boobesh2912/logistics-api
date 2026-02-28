from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
