import enum
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    Index,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
)
from datetime import datetime
from .Auth import Auth
from ..constants import VerificationTypeEnum


class AuthVerification(Auth):
    __tablename__ = "auth_verifications"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    code = Column(String(6), nullable=False)  # 6-digit verification code
    type = Column(Enum(VerificationTypeEnum), nullable=False)
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    attempts = Column(Integer, default=0)  # Track failed attempts

    __table_args__ = (
        Index("idx_auth_verifications_user_type", "user_id", "type"),
        Index("idx_auth_verifications_expires", "expires_at"),
    )

    # Relationship to user
    user = relationship("User", back_populates="verifications")
