from pydantic import BaseModel
from typing import Optional


class AppSettings(BaseModel):
    # Database settings
    db_host: str = "db"  # Changed from postgres to db to match service name
    db_port: int = 5432
    db_user: str = "postgres"  # Match POSTGRES_USER
    db_pass: str = "postgres"  # Match POSTGRES_PASSWORD
    db_name: str = "postgres"  # Match POSTGRES_DB
    database_url: Optional[str] = None

    # Redis settings
    redis_host: str = "redis"  # Changed from localhost to redis for Docker
    redis_port: int = 6379

    # API settings
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    debug: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.database_url:
            self.database_url = (
                f"postgresql://{self.db_user}:{self.db_pass}@"
                f"{self.db_host}:{self.db_port}/{self.db_name}"
            )


app_settings = AppSettings()
