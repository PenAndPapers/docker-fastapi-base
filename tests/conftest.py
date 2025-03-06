import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.core.config import AppSettings


@pytest.fixture
def db_session():
    # Use test-specific database settings
    test_settings = AppSettings(
        db_host="localhost",
        db_port=5432,
        db_user="postgres",
        db_pass="postgres",
        db_name="postgres",
    )

    engine = create_engine(test_settings.database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    # Base.metadata.drop_all(engine)  # Commented out to preserve the data
