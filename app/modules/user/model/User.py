from sqlalchemy import Column, Integer, Boolean, String, DateTime, text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    address = Column(String, nullable=True)
    role = Column(String, nullable=True, server_default="user")
    status = Column(String, nullable=True, server_default="offline")
    is_verified = Column(Boolean, server_default=text("false"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Add relationship to UserToken
    tokens = relationship(
        "UserToken", back_populates="user", cascade="all, delete-orphan"
    )
