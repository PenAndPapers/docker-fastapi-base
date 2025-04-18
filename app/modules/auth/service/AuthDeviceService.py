from ..repository import AuthDeviceRepository
from ..schema import DeviceInfo, DeviceRequest, DeviceResponse

class AuthDeviceService:
  def __init__(self, repository: AuthDeviceRepository):
    self.repository = repository

  def store_device(self, user_id: int, device: DeviceInfo) -> DeviceResponse:
        """Handle user device information and storage"""

        # Store device information
        stored_device = self.repository.store_device(
            DeviceRequest(
                user_id=user_id,
                device_id=device.device_id,
                client_info=device.client_info,
            )
        )

        return stored_device