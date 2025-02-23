from sqlalchemy.orm import Session
from typing import List, Optional
from ..model import {Module}Model


class {Module}Repository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, _{module}: {Module}Model) -> {Module}Model:
        pass

    def get_all(self) -> List[{Module}Model]:
        pass

    def get_by_id(self, id: int) -> Optional[{Module}Model]:
        pass

    def update(self, _{module}: {Module}Model) -> {Module}Model:
        pass

    def delete(self, _{module}: {Module}Model) -> bool:
        pass
