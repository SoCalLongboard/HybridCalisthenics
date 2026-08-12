from typing import Iterator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import SESSION_MAX_AGE
from app.db import SessionLocal
from app.models import User
from app.security import COOKIE_NAME, read_session_token


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = read_session_token(token, max_age=SESSION_MAX_AGE)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user
