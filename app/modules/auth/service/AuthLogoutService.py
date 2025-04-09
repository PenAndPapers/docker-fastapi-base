from typing import Any
from ..repository import AuthRepository

class AuthLogoutService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository


    def logout(self, data: Any) -> None:
        """Logout user"""
        # TODO: Implement logout logic
        pass