from sqlalchemy import Column, Integer, Boolean, String, DateTime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String, min_length=8)
    first_name = Column(String)
    last_name = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
