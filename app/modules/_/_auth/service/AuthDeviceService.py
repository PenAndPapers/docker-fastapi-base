from ..repository import AuthDeviceRepository
from ..schema import DeviceInfo, DeviceRequest, DeviceResponse

class AuthDeviceService:
  def __init__(self, repository: AuthDeviceRepository):
    self.repository = repository

  def create(self, user_id: int, device: DeviceInfo) -> DeviceResponse:
      """Handle user device information and storage"""

      # Store device information
      stored_device = self.repository.create(
          DeviceRequest(
              user_id=user_id,
              device_id=device.device_id,
              client_info=device.client_info,
          )
      )

      return stored_device


  def get(self):
      """Get user device information"""
      pass


  def update(self):
      """Update user device information"""
      pass


  def delete(self):
      """Delete user device information"""
      pass