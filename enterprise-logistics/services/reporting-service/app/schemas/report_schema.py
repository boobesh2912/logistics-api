from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class ReportResponse(BaseModel):
    total_shipments_today: int
    delivered: int
    in_transit: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    role: str
