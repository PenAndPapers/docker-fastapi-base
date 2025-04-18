from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    Index,
    String,
    DateTime,
    ForeignKey,
    Enum,
    CheckConstraint,
    text,
)
from .AuthBaseModel import AuthBaseModel
from ..constants import OneTimePinTypeEnum


class AuthOneTimePinModel(AuthBaseModel):
    __tablename__ = "auth_one_time_pins"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token_id = Column(Integer, ForeignKey("auth_tokens.id", ondelete="CASCADE"))
    device_id = Column(Integer, ForeignKey("auth_devices.id", ondelete="CASCADE"))
    code = Column(String(6), unique=True, nullable=False)
    type = Column(Enum(OneTimePinTypeEnum), nullable=False)
    attempts = Column(Integer, server_default=text("0"))
    expires_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False,)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_auth_one_time_pins_user_type", "user_id", "type"),
        Index("idx_auth_one_time_pins_expires", "expires_at"),
        Index("idx_auth_one_time_pins_token", "token_id"),
        Index("idx_auth_one_time_pins_device", "device_id"),
        CheckConstraint("attempts <= 3", name="check_max_attempts"),
    )

    # Relationships
    user = relationship("UserModel", back_populates="one_time_pins")
    token = relationship("AuthTokenModel", back_populates="one_time_pins")
    device = relationship("AuthDeviceModel", back_populates="one_time_pins")
