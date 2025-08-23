from sqlalchemy import Column, String, DECIMAL, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from ..base import Base


class DiscountType(enum.Enum):
    percentage = "percentage"
    fixed = "fixed"


class OrderDiscount(Base):
    __tablename__ = "order_discounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    type = Column(SQLEnum(DiscountType), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(String(255), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    applied_at = Column(DateTime, default=datetime.now(timezone.utc))

    order = relationship("Order", back_populates="order_discounts")
    staff = relationship("User")