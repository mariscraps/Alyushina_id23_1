from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# создаем движок, через который SQLAlchemy будет работать с бд
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db  # отдаем сессию вызывающему коду (например в маршруте)
    finally:
        db.close()
