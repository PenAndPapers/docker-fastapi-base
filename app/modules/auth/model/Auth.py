from app.database import Base


class Auth(Base):
    # __tablename__ = "auth"
    __abstract__ = True
    pass
