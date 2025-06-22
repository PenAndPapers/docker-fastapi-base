from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    text,
)
from datetime import datetime
from app.database import Base


class DeviceModel(Base):
    __tablename__ = "device"
  
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False)
    client_info = Column(String(255), nullable=False)
    last_login = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
