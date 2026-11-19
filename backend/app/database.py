from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

DATABASE_URL = settings.database_url

engine=create_engine(
    DATABASE_URL,
    echo=settings.sql_echo,
    pool_pre_ping=True,
)

SessionLocal=sessionmaker(
bind=engine,
autoflush=False,
)
 ##Base == базовый класс ORM - моделей 
class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session
        
