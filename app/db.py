import os

from sqlalchemy import create_engine, inspect, text
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


def run_migrations() -> None:
    """Hand-rolled migration for columns added to existing tables.

    Base.metadata.create_all only creates missing tables, it never alters
    existing ones, so columns added to the User model after this app has
    real data on disk need to be applied here.
    """
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return  # fresh DB — create_all will build the table with all current columns

    existing = {c["name"] for c in inspector.get_columns("users")}
    ddl = {
        "is_admin": "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0",
        "is_active": "ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1",
        "must_change_password": "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN NOT NULL DEFAULT 0",
        "last_login_at": "ALTER TABLE users ADD COLUMN last_login_at DATETIME",
    }
    added_is_admin = "is_admin" not in existing
    with engine.begin() as conn:
        for col, stmt in ddl.items():
            if col not in existing:
                conn.execute(text(stmt))
        if added_is_admin:
            # Upgrading an install that predates admin support: promote the
            # earliest-created user so the system isn't left with zero admins.
            conn.execute(text("UPDATE users SET is_admin = 1 WHERE id = (SELECT MIN(id) FROM users)"))


def init_db() -> None:
    run_migrations()
    Base.metadata.create_all(engine)
