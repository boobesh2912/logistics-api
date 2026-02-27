# app/models/tracking.py
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class TrackingUpdate(Base):
    __tablename__ = "tracking_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id"), nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now())

    shipment = relationship("Shipment", back_populates="tracking_updates")