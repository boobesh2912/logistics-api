from sqlalchemy import Column, String, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tracking_number = Column(String, unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # assigned by admin
    source_address = Column(Text, nullable=False)
    destination_address = Column(Text, nullable=False)
    status = Column(
        Enum("created", "in_transit", "out_for_delivery", "delivered", name="shipment_status"),
        default="created",
        nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.now())

    tracking_updates = relationship("TrackingUpdate", back_populates="shipment", cascade="all, delete-orphan")