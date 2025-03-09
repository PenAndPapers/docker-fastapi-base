from sqlalchemy import Column, Integer, String, Enum, DateTime, text
from app.database import Base
from ..constants import TodoSeverityEnum, TodoStatusEnum


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    severity = Column(
        Enum(TodoSeverityEnum, name="TodoSeverityEnum", create_type=False),
        nullable=False,
        server_default=TodoSeverityEnum.LOW.name,
    )
    status = Column(
        Enum(TodoStatusEnum, name="TodoStatusEnum", create_type=False),
        nullable=False,
        server_default=TodoStatusEnum.TODO.name,
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
    deleted_at = Column(DateTime(timezone=True), nullable=True)
