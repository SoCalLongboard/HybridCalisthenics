import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_PATH
from app.models import Base

db_dir = os.path.dirname(DATABASE_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)
