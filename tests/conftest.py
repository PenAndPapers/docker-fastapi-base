import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base  # Updated import


@pytest.fixture
def db_session():
    # Setup test database
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)
