from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.database import Base


class UserModel(Base):
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
    uuid = Column(String, default=lambda: str(uuid4()), unique=True, nullable=False)
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
    verified_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tokens = relationship(
        "AuthTokenModel", back_populates="user", cascade="all, delete-orphan"
    )
    devices = relationship(
        "AuthDeviceModel", back_populates="user", cascade="all, delete-orphan"
    )
    one_time_pins = relationship(
        "AuthOneTimePinModel", back_populates="user", cascade="all, delete-orphan"
    )
