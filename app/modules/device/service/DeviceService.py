from ..repository import DeviceRepository
from ..schema import DeviceRequest, DeviceResponse

class DeviceService:
  def __init__(self, repository: DeviceRepository):
    self.repository = repository

  def create(self, device: DeviceRequest) -> DeviceResponse:
      """Handle user device information and storage"""
      stored_device = self.repository.create(device)

      return stored_device


  def get(self, id: int) -> DeviceResponse:
      """Get user device information"""
      device = self.repository.get(id)
      
      return device

  def update(self) -> DeviceResponse:
      """Update user device information"""
      pass


  def delete(self) -> None:
      """Delete user device information"""
      pass