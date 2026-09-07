from fastapi import APIRouter, Depends

from app.catalog import load_catalog
from app.deps import get_current_active_user
from app.models import User

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("")
def get_catalog(user: User = Depends(get_current_active_user)) -> dict:
    return load_catalog()
