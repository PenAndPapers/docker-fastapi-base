from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean


class Auth(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
