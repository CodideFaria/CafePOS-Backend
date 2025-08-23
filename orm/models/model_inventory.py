from sqlalchemy import Column, String, DECIMAL, DateTime, Text, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum
from ..base import Base


class InventoryStatus(enum.Enum):
    in_stock = "in_stock"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"
    expired = "expired"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    current_stock = Column(DECIMAL(10, 3), nullable=False, default=0)
    min_stock_level = Column(DECIMAL(10, 3), nullable=False, default=0)
    max_stock_level = Column(DECIMAL(10, 3), nullable=False, default=100)
    unit = Column(String(20), nullable=False)  # kg, liters, pieces, boxes, etc.
    cost_per_unit = Column(DECIMAL(10, 4), nullable=False, default=0)
    supplier = Column(String(100), nullable=True)
    last_restocked = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    barcode = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    @property
    def status(self):
        if self.expiry_date and self.expiry_date < datetime.now(timezone.utc):
            return InventoryStatus.expired.value
        elif self.current_stock <= 0:
            return InventoryStatus.out_of_stock.value
        elif self.current_stock <= self.min_stock_level:
            return InventoryStatus.low_stock.value
        else:
            return InventoryStatus.in_stock.value
