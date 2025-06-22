from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..model import DeviceModel
from ..schema import DeviceRequest, DeviceResponse


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db
        self.device_repository = DatabaseRepository(db, DeviceModel)


    def create(self, data: DeviceRequest) -> DeviceResponse:
        """Store device info"""
        device = self.device_repository.create(data)
        return DeviceResponse.model_validate(device)


    def get(self):
        """Get device info"""
        pass


    def update(self):
        """Update device info"""
        pass


    def delete(self):
        """Delete device info"""
        pass


    def invalidate_user_devices(self, user_id: int) -> None:
        """Invalidate all existing devices for a user"""
        self.device_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()