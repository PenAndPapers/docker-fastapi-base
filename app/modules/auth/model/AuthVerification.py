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
from .Auth import Auth
from ..constants import VerificationTypeEnum


class AuthVerification(Auth):
    __tablename__ = "auth_verifications"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token_id = Column(Integer, ForeignKey("auth_tokens.id", ondelete="CASCADE"))
    device_id = Column(Integer, ForeignKey("auth_devices.id", ondelete="CASCADE"))
    code = Column(String(6), nullable=False)  # 6-digit verification code
    type = Column(Enum(VerificationTypeEnum), nullable=False)
    attempts = Column(Integer, server_default=text("0"))  # Track failed attempts (max 3)
    expires_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False,)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_auth_verifications_user_type", "user_id", "type"),
        Index("idx_auth_verifications_expires", "expires_at"),
        Index("idx_auth_verifications_token", "token_id"),
        Index("idx_auth_verifications_device", "device_id"),
        CheckConstraint("attempts <= 3", name="check_max_attempts"),
    )

    # Relationships
    user = relationship("User", back_populates="verifications")
    token = relationship("AuthToken", back_populates="verifications")
    device = relationship("AuthDevice", back_populates="verifications")
