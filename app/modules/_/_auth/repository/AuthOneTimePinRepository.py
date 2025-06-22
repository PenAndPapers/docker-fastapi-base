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

    def create(self, data: VerificationRequest) -> VerificationResponse:
        """
        Store user's one time pin
        
        Args:
            data (VerificationRequest): One time pin data

        Returns:
            VerificationResponse: One time pin response
        """
        otp = self.one_time_pin_repository.create(data)

        return VerificationResponse(**vars(otp)) if otp else None


    def get(self, filter_dict: dict) -> VerificationResponse:
        """
        Get user's one time pin

        Args:
            filter_dict (dict): One time pin filter dict

        Returns:
            VerificationResponse: One time pin response
        """
        otp = self.one_time_pin_repository.get_one_by_filter(filter_dict)

        return VerificationResponse(**vars(otp))


    def update(self, otp_data: VerificationUpdateRequest) -> VerificationResponse:
        """
        Update user's one time pin
        
        Args:
            otp_data (VerificationUpdateRequest): One time pin data
            
        Returns:
            VerificationResponse: One time pin response
        """
        updated_otp = self.one_time_pin_repository.update(
            otp_data.id, otp_data
        )

        return VerificationResponse(**vars(updated_otp)) if updated_otp else None


    def delete(self) -> None:
        """Invalidate/delete user's one time pin"""
        # TODO
        pass