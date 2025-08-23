from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime, timezone
from ..base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(50), primary_key=True)  # e.g., 'menu.view'
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))