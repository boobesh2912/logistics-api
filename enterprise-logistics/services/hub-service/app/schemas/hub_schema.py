from pydantic import BaseModel, ConfigDict
from uuid import UUID


class HubCreate(BaseModel):
    hub_name: str
    city: str


class HubUpdate(BaseModel):
    hub_name: str | None = None
    city: str | None = None


class HubResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    hub_name: str
    city: str
