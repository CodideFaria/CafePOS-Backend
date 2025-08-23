from sqlalchemy import Column, String, DECIMAL, DateTime, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from ..base import Base


class PaymentMethod(enum.Enum):
    cash = "cash"
    card = "card"


class OrderStatus(enum.Enum):
    completed = "completed"
    refunded = "refunded"
    voided = "voided"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(20), unique=True, nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    cash_received = Column(DECIMAL(10, 2), default=0)
    change_amount = Column(DECIMAL(10, 2), default=0)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.completed)
    staff_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    customer_name = Column(String(100), nullable=True)
    customer_email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    reprint_count = Column(Integer, default=0)
    last_reprint = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    staff = relationship("User")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    order_discounts = relationship("OrderDiscount", back_populates="order", cascade="all, delete-orphan")
