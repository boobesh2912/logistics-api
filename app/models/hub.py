# app/models/hub.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class Hub(Base):
    __tablename__ = "hubs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hub_name = Column(String, nullable=False)
    city = Column(String, nullable=False)