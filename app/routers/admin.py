import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_admin, get_db
from app.models import User
from app.schemas import AdminPasswordResetOut, AdminUserOut
from app.security import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _count_admins(db: Session) -> int:
    return db.query(User).filter(User.is_admin.is_(True)).count()


def _get_target_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _require_not_self(admin: User, target: User) -> None:
    if target.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot perform this action on your own account")


def _require_not_last_admin(db: Session, target: User) -> None:
    if target.is_admin and _count_admins(db) <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the last admin")


@router.get("/users", response_model=list[AdminUserOut])
def list_users(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.id).all()


@router.post("/users/{user_id}/disable", response_model=AdminUserOut)
def disable_user(
    user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
) -> User:
    target = _get_target_user(db, user_id)
    _require_not_self(admin, target)
    _require_not_last_admin(db, target)

    target.is_active = False
    db.commit()
    db.refresh(target)
    return target


@router.post("/users/{user_id}/enable", response_model=AdminUserOut)
def enable_user(
    user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
) -> User:
    target = _get_target_user(db, user_id)
    target.is_active = True
    db.commit()
    db.refresh(target)
    return target


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> None:
    target = _get_target_user(db, user_id)
    _require_not_self(admin, target)
    _require_not_last_admin(db, target)

    db.delete(target)
    db.commit()


@router.post("/users/{user_id}/promote", response_model=AdminUserOut)
def promote_user(
    user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
) -> User:
    target = _get_target_user(db, user_id)
    target.is_admin = True
    db.commit()
    db.refresh(target)
    return target


@router.post("/users/{user_id}/demote", response_model=AdminUserOut)
def demote_user(
    user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
) -> User:
    target = _get_target_user(db, user_id)
    _require_not_self(admin, target)
    _require_not_last_admin(db, target)

    target.is_admin = False
    db.commit()
    db.refresh(target)
    return target


@router.post("/users/{user_id}/reset-password", response_model=AdminPasswordResetOut)
def reset_password(
    user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
) -> AdminPasswordResetOut:
    target = _get_target_user(db, user_id)

    temporary_password = secrets.token_urlsafe(12)
    target.password_hash = hash_password(temporary_password)
    target.must_change_password = True
    db.commit()

    return AdminPasswordResetOut(temporary_password=temporary_password)
