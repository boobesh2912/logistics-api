from sqlalchemy import Column, String, Text, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_number = Column(String, nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    source_address = Column(Text, nullable=False)
    destination_address = Column(Text, nullable=False)
    status = Column(
        Enum("created", "in_transit", "out_for_delivery", "delivered", name="shipment_status"),
        default="created",
        nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
