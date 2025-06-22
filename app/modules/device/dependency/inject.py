from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..repository import DeviceRepository
from ..service import DeviceService

# Inject Repositories
def get_device_repository(db: Session = Depends(get_db)) -> DeviceRepository:
    return DeviceRepository(db)

# Inject Services
def get_auth_device_service(
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceService:
    return DeviceService(repository)