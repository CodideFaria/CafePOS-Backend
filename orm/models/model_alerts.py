from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from ..base import Base


class Alerts(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey('inventory_items.id'), nullable=False)
    alert_time = Column(DateTime, default=datetime.now(timezone.utc))
    alert_type = Column(String(100), nullable=False) # e.g., "low_stock"
    notification_sent = Column(Boolean, default=False)
    notification_method = Column(String(50))

    inventory_item = relationship("InventoryItem")

