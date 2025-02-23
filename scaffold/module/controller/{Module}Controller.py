from typing import List
from ..service.{Module}Service import {Module}Service
from ..schema import {Module}Create, {Module}Update, {Module}Response


class {Module}Controller:
    def __init__(self, service: {Module}Service):
        self.service = service

    def create(self, data: {Module}Create) -> {Module}Response:
        pass

    def get_all(self) -> List[{Module}Response]:
        pass

    def get_by_id(self, id: int) -> {Module}Response:
        pass

    def update(self, id: int, data: {Module}Update) -> {Module}Response:
        pass

    def delete(self, id: int) -> None:
        pass
