from typing import Any
from ..repository import AuthUserRepository

class AuthLogoutService:
    def __init__(self, repository: AuthUserRepository):
        self.repository = repository


    def logout(self, data: Any) -> None:
        """Logout user"""
        # TODO: Implement logout logic
        pass