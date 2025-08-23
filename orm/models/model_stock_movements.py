from sqlalchemy import Column, String, DECIMAL, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from ..base import Base


class MovementType(enum.Enum):
    restock = "restock"
    usage = "usage"
    waste = "waste"
    adjustment = "adjustment"


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False)
    type = Column(SQLEnum(MovementType), nullable=False)
    quantity = Column(DECIMAL(10, 3), nullable=False)  # positive for add, negative for remove
    previous_stock = Column(DECIMAL(10, 3), nullable=False)
    new_stock = Column(DECIMAL(10, 3), nullable=False)
    reason = Column(String(255), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    cost = Column(DECIMAL(10, 2), nullable=True)
    supplier = Column(String(100), nullable=True)
    reference_order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    inventory_item = relationship("InventoryItem")
    staff = relationship("User")
    reference_order = relationship("Order")