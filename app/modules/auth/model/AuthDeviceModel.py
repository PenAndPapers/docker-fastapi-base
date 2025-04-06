from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship
from .Auth import Auth


class AuthDeviceModel(Auth):
    __tablename__ = "auth_devices"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    device_id = Column(String(255), nullable=False)
    client_info = Column(String(255), nullable=False)
    last_login = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (UniqueConstraint("user_id", "device_id", name="uq_user_device"),)

    # Relationship to user
    user = relationship("User", back_populates="devices")

    # Add this relationship
    verifications = relationship("AuthVerification", back_populates="device")
