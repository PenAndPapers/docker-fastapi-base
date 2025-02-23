from typing import List
from ..repository.{Module}Repository import {Module}Repository
from ..model import {Module}
from ..schema import {Module}Create, {Module}Update
from .{Module}Policy import {Module}Policy


class {Module}Service:
    def __init__(self, repository: {Module}Repository, policy: {Module}Policy):
        self.repository = repository
        self.policy = policy

    def create(self, data: {Module}Create) -> {Module}:
        """Create a new record."""
        return self.repository.create(data)

    def get_all(self) -> List[{Module}]:
        """Get all record."""
        return self.repository.get_all()

    def get_by_id(self, id: int) -> {Module}:
        """Get a record by its ID."""
        return self.repository.get_by_id(id)

    def update(self, id: int, data: {Module}Update) -> {Module}:
        """Update a record by its ID."""
        self.get_by_id(id)
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        """Delete a record by its ID."""
        self.get_by_id(id)
        return self.repository.delete(id)
