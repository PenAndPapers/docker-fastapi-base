from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, Index
from sqlalchemy.orm import relationship
from .Auth import Auth


class AuthToken(Auth):
    __tablename__ = "auth_tokens"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_auth_tokens_expires_at", "expires_at"),)

    # Relationship to user
    user = relationship("User", back_populates="auth_tokens")

    # Relationship to verification
    verification = relationship(
        "AuthVerification", 
        uselist=False,  # one-to-one relationship
        back_populates="token",
        cascade="all, delete-orphan"
    )
