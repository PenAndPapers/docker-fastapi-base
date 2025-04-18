from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..model import AuthOneTimePinModel
from ..schema import (
    VerificationRequest,
    VerificationUpdateRequest,
    VerificationResponse,
)


class AuthOneTimePinRepository:
    def __init__(self, db: Session):
        self.db = db
        self.one_time_pin_repository = DatabaseRepository(db, AuthOneTimePinModel)

    def store_one_time_pin(
        self,
        otp_data: VerificationRequest
    ) -> VerificationResponse:
        """
        Store one time pin
        
        Args:
            otp_data (VerificationRequest): One time pin data

        Returns:
            VerificationResponse: One time pin response
        """
        otp = self.one_time_pin_repository.create(otp_data)

        return VerificationResponse(**vars(otp)) if otp else None

    def get_one_time_pin(
        self, otp_filter_dict: dict
    ) -> VerificationResponse:
        """
        Get one time pin

        Args:
            otp_filter_dict (dict): One time pin filter dict

        Returns:
            VerificationResponse: One time pin response
        """
        otp = self.one_time_pin_repository.get_by_filter(otp_filter_dict)

        return VerificationResponse(**vars(otp)) if otp else None

    def update_one_time_pin(
        self, otp_data: VerificationUpdateRequest
    ) -> VerificationResponse:
        """
        Update one time pin
        
        Args:
            otp_data (VerificationUpdateRequest): One time pin data
            
        Returns:
            VerificationResponse: One time pin response
        """
        updated_otp = self.one_time_pin_repository.update(
            otp_data.id, otp_data
        )

        return VerificationResponse(**vars(updated_otp)) if updated_otp else None

    def invalidate_one_time_pin(self) -> None:
        """Invalidate one time pin"""
        # TODO: Implement
        pass