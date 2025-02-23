from sqlalchemy import Column, Integer, String, Enum, DateTime, text
from app.database import Base
from ..constants import SeverityEnum, StatusEnum


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    severity = Column(
        Enum(SeverityEnum, name="severityenum", create_type=False),
        nullable=False,
        server_default=SeverityEnum.LOW.name,
    )
    status = Column(
        Enum(StatusEnum, name="statusenum", create_type=False),
        nullable=False,
        server_default=StatusEnum.TODO.name,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
