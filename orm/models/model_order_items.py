from sqlalchemy import Column, String, DECIMAL, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from ..base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), nullable=False)
    menu_item_name = Column(String(100), nullable=False)  # Snapshot at time of sale
    menu_item_size = Column(String(50), nullable=False)   # Snapshot at time of sale
    unit_price = Column(DECIMAL(10, 2), nullable=False)   # Price at time of sale
    quantity = Column(Integer, nullable=False)
    line_total = Column(DECIMAL(10, 2), nullable=False)   # unit_price * quantity
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem")
