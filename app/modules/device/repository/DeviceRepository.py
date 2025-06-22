from sqlalchemy import Boolean
from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..model import DeviceModel
from ..schema import DeviceFilter, DeviceRequest, DeviceResponse


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db
        self.device_repository = DatabaseRepository(db, DeviceModel)


    def create(self, data: DeviceRequest) -> DeviceResponse:
        """Store device info"""
        device = self.device_repository.create(data)
        return DeviceResponse.model_validate(device)


    def get(self, id: int) -> DeviceResponse:
        """Get device info"""
        device = self.device_repository.get_one(id)
        return DeviceResponse.model_validate(device)
        

    def update(self):
        """Update device info"""
        pass


    def delete(self, id: int) -> Boolean:
        """Delete device info"""
        return self.device_repository.delete(id)


    def invalidate_user_devices(self, user_id: int) -> None:
        """Invalidate all existing devices for a user"""
        filter = DeviceFilter(user_id=user_id)
        self.device_repository.delete_by_filter(filter)
        self.db.flush()