from sqlalchemy.orm import Session
from typing import List, Optional
from ..model import {Module}


class {Module}Repository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, _{module}: {Module}) -> {Module}:
        pass

    def get_all(self) -> List[{Module}]:
        pass

    def get_by_id(self, id: int) -> Optional[{Module}]:
        pass

    def update(self, _{module}: {Module}) -> {Module}:
        pass

    def delete(self, _{module}: {Module}) -> bool:
        pass
