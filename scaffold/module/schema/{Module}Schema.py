from pydantic import BaseModel
from datetime import datetime


class {Module}Base(BaseModel):
    pass


class {Module}Create({Module}Base):
    pass


class {Module}Update({Module}Base):
    pass


class {Module}Response({Module}Base):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
