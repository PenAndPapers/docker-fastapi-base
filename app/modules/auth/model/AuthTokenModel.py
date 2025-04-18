from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .AuthBaseModel import AuthBaseModel


class AuthTokenModel(AuthBaseModel):
    __tablename__ = "auth_tokens"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    __table_args__ = (Index("idx_auth_tokens_expires_at", "expires_at"),)

    # Relationship to user
    user = relationship("UserModel", back_populates="tokens")

    # Relationship to one time pin
    one_time_pins = relationship("AuthOneTimePinModel", back_populates="token")
