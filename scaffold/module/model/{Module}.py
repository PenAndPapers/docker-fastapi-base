from sqlalchemy import Column, Integer
from app.database import Base


class {Module}(Base):
    __tablename__ = "{module}s"

    id = Column(Integer, primary_key=True, index=True)
    # Add your columns here
    pass
