from pydantic import BaseModel
from datetime import datetime
from .{Module}Base import {Module}Base


class {Module}Response({Module}Base):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
