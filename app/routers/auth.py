from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import SECURE_COOKIES, SESSION_MAX_AGE
from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, UserOut
from app.security import COOKIE_NAME, create_session_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, user_id: int) -> None:
    token = create_session_token(user_id)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=SECURE_COOKIES,
        max_age=SESSION_MAX_AGE,
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    db.refresh(user)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    _set_session_cookie(response, user.id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
