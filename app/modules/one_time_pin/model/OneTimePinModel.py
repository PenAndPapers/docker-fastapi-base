from sqlalchemy import (
    Column,
    Integer,
    Enum,
    String,
    DateTime,
    Index,
    ForeignKey,
    CheckConstraint,
    text,
)
from datetime import datetime
from app.database import Base
from ..constants import EnumOneTimePinType


class OneTimePinModel(Base):
    __tablename__ = "one_time_pin"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False)
    type = Column(Enum(EnumOneTimePinType), nullable=False)
    attempts = Column(Integer, server_default=text("0"))
    expires_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False,)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)