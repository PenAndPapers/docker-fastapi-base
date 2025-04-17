from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..schema import (
    DeviceRequest,
    DeviceResponse,
)


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.device_repository = DatabaseRepository(db, AuthDeviceModel)

    def store_device(self, data: DeviceRequest) -> DeviceResponse:
        """Store device info"""
        device = self.device_repository.create(data)
        return DeviceResponse.model_validate(device)

    def invalidate_user_devices(self, user_id: int) -> None:
        """Invalidate all existing devices for a user"""
        self.device_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()