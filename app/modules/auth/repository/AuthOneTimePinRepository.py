from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..model import AuthOneTimePinModel
from ..schema import (
    VerificationRequest,
    VerificationUpdateRequest,
    VerificationResponse,
)


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.one_time_pin_repository = DatabaseRepository(db, AuthOneTimePinModel)

    def store_verification_code(
        self,
        verification_data: VerificationRequest
    ) -> VerificationResponse:
        """Store verification code"""
        verification = self.verification_repository.create(verification_data)
        return VerificationResponse(**vars(verification))

    def get_verification_code(
        self, filter_dict: dict
    ) -> VerificationResponse:
        """Get verification code and increment attempt counter"""
        verification = self.verification_repository.get_by_filter(filter_dict)

        if verification:
            # Convert SQLAlchemy model to dict, then to VerificationResponse
            return VerificationResponse(**vars(verification))

        return None

    def update_verification_code(
        self, verification: VerificationUpdateRequest
    ) -> VerificationResponse:
        """Update verification code"""
        updated_verification = self.verification_repository.update(
            verification.id, verification
        )

        return VerificationResponse(**vars(updated_verification))

    def invalidate_verification_code(self) -> None:
        """Invalidate verification code"""
        # TODO: Implement
        pass